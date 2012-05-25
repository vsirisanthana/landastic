//angular.module('Landastic', ['ngResource']);

angular.module('Landastic', ['ngResource']).
    config(['$routeProvider', function($routeProvider) {
        $routeProvider.
            when('/', {template: '/templates/partials/list.html', controller: LandListCtrl}).
            when('/add', {template: '/templates/partials/edit.html', controller: LandAddCtrl}).
            when('/edit/:key', {template: '/templates/partials/edit.html', controller: LandEditCtrl}).
            otherwise({redirectTo: '/'});
    }]);

//angular.module('Landastic', ['ngResource']).
//    config(['$locationProvider', function($locationProvider) {
//        $locationProvider.html5Mode(false);
//        $locationProvider.hashPrefix('!');
//    }]);


function MainCtrl($scope, $resource) {

    // Resources
    $scope.Land = $resource('/api/lands/:key', {key: '@key'}, {update: {method: 'PUT'}});

    // Google Maps
    $scope.defaultLocation = new google.maps.LatLng(18.769668, 99.003057);
    $scope.map = new google.maps.Map(document.getElementById("map_canvas"), {
        center: $scope.defaultLocation,
        zoom: 8,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    $scope.drawingManager = new google.maps.drawing.DrawingManager({
        drawingControlOptions: {
            drawingModes: [
                google.maps.drawing.OverlayType.MARKER,
                google.maps.drawing.OverlayType.CIRCLE
            ]
        },
        markerOptions: {
            draggable: true
        },
        circleOptions: {
            editable: true
        }
    });
    $scope.drawingManager.setMap($scope.map);


//    $scope.deleteLand = function(land) {
//        land.$delete();
//    };




    $scope.deleteOverlays = function(overlays) {
        if (overlays) {
            angular.forEach(overlays, function(overlay) {
                overlay.setMap(null);
            });
            overlays.length = 0;
        }
    };

    $scope.showOverlays = function(overlays) {
        if (overlays) {
            angular.forEach(overlays, function(overlay) {
                overlay.setMap($scope.map);
            });
        }
    };
}


function LandListCtrl($scope) {

    $scope.overlays = [];

    $scope.$on('$beforeRouteChange', function() {
        $scope.deleteOverlays($scope.overlays);
    });

    $scope.lands = $scope.Land.query({}, function() {
        $scope.overlays = $scope.lands.map(function(land) {
            var location = land.location.split(',');
            var latLng = new google.maps.LatLng(location[0], location[1]);
            return new google.maps.Marker({
                icon: '/static/img/drw-ToolCircleLarge.png',
                position: latLng,
                title: land.name
            });
        });
        $scope.showOverlays($scope.overlays);
        $scope.map.fitBounds(getBounds($scope.overlays));
    });

    $scope.drawingManager.setOptions({
        drawingMode: null,
        drawingControl: false
    });

    google.maps.event.clearListeners($scope.drawingManager, 'markercomplete');
    google.maps.event.clearListeners($scope.drawingManager, 'circlecomplete');


}

function LandAddCtrl($scope, $location) {

    $scope.$location = $location;

    $scope.$on('$beforeRouteChange', function() {
        $scope.deleteOverlays($scope.overlays);
    });


    $scope.activeLand = new $scope.Land();
    $scope.drawingManager.setOptions({drawingControl: true});

    $scope.overlays = [];

    $scope.$watch('overlays.length', function() {
        $scope.activeLand.features = serializeOverlays($scope.overlays);

        var center = getBounds($scope.overlays).getCenter();
        $scope.activeLand.location = center.lat() + ',' + center.lng();
    });

    google.maps.event.addListener($scope.drawingManager, 'markercomplete', function(marker) {
        $scope.overlays.push(marker);
        $scope.$apply();
    });

    google.maps.event.addListener($scope.drawingManager, 'circlecomplete', function(circle) {
        $scope.overlays.push(circle);
        $scope.$apply();
    });

    $scope.saveLand = function() {
        $scope.activeLand.$save({}, function() {
            $location.path('/');
        }, function() {
            console.log('error adding');
        });
    };
}

function LandEditCtrl($scope, $location, $routeParams) {


    $scope.$location = $location;

    $scope.$on('$beforeRouteChange', function() {
        $scope.deleteOverlays($scope.overlays);
    });


    $scope.drawingManager.setOptions({drawingControl: true});


    $scope.overlays = [];


    $scope.$watch('overlays.length', function() {
        $scope.activeLand.features = serializeOverlays($scope.overlays);
        var center = getBounds($scope.overlays).getCenter();
        $scope.activeLand.location = center.lat() + ',' + center.lng();
    });

    $scope.activeLand = $scope.Land.get({key: $routeParams.key}, function() {
        $scope.overlays = deserializeOverlays($scope.activeLand.features);
        $scope.showOverlays($scope.overlays);
        $scope.map.fitBounds(getBounds($scope.overlays));
    });

    google.maps.event.addListener($scope.drawingManager, 'markercomplete', function(marker) {
        $scope.overlays.push(marker);
        $scope.$apply();
    });

    google.maps.event.addListener($scope.drawingManager, 'circlecomplete', function(circle) {
        $scope.overlays.push(circle);
        $scope.$apply();
    });

    $scope.saveLand = function() {
        $scope.activeLand.$update({}, function() {
            $location.path('/');
        }, function() {
            console.log('error updating');
        });
    };
}