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


function MainCtrl($scope, $location, $resource) {

    $scope.$location = $location;

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
                google.maps.drawing.OverlayType.CIRCLE,
                google.maps.drawing.OverlayType.POLYGON
            ]
        },
        markerOptions: {
            draggable: true
        },
        circleOptions: {
            editable: true
        },
        polygonOptions: {
            editable: true
        }
    });
    $scope.drawingManager.setMap($scope.map);
}

function LandBaseCtrl($scope) {
    $scope.$on('$beforeRouteChange', function() {
        if ($scope.overlays) {
            $scope.overlays.clear();
        }
    });
}

function LandListCtrl($scope) {

    LandBaseCtrl($scope);

    $scope.lands = $scope.Land.query(function() {
        $scope.overlays = new OverlayArray($scope.lands.map(function(land) {
            var location = land.location.split(',');
            var latLng = new google.maps.LatLng(location[0], location[1]);
            return new google.maps.Marker({
                icon: '/static/img/drw-ToolCircleLarge.png',
                position: latLng,
                title: land.name
            });
        }));
        $scope.overlays.setMap($scope.map);
        $scope.map.fitBounds($scope.overlays.getBounds());
    });

    $scope.drawingManager.setOptions({
        drawingMode: null,
        drawingControl: false
    });

    google.maps.event.clearListeners($scope.drawingManager, 'markercomplete');
    google.maps.event.clearListeners($scope.drawingManager, 'circlecomplete');

}

function LandAddEditBaseCtrl($scope) {
    LandBaseCtrl($scope);

    $scope.$on('overlaysChange', function() {
        var center = $scope.overlays.getBounds().getCenter();
        $scope.land.location = center.lat() + ',' + center.lng();
        $scope.land.features = JSON.stringify($scope.overlays.toObj());
    });

    $scope.broadcastOverlaysChangeEvent = function() {
        $scope.$broadcast('overlaysChange');
        $scope.$apply();
    };

    google.maps.event.addListener($scope.drawingManager, 'markercomplete', function(marker) {
        google.maps.event.addListener(marker, 'dragend', $scope.broadcastOverlaysChangeEvent);
        google.maps.event.addListener(marker, 'click', function() {
            var infoWindow = new google.maps.InfoWindow({
                content: '<button class="btn">Delete</button>'
            });
            infoWindow.open($scope.map, marker);
        });
        $scope.overlays.push(marker);
        $scope.broadcastOverlaysChangeEvent();
    });

    google.maps.event.addListener($scope.drawingManager, 'circlecomplete', function(circle) {
        google.maps.event.addListener(circle, 'center_changed', $scope.broadcastOverlaysChangeEvent);
        google.maps.event.addListener(circle, 'radius_changed', $scope.broadcastOverlaysChangeEvent);
        $scope.overlays.push(circle);
        $scope.broadcastOverlaysChangeEvent();
    });

    google.maps.event.addListener($scope.drawingManager, 'polygoncomplete', function(polygon) {
        angular.forEach(polygon.getPaths(), function(path) {
            google.maps.event.addListener(path, 'set_at', $scope.broadcastOverlaysChangeEvent);
            google.maps.event.addListener(path, 'insert_at', $scope.broadcastOverlaysChangeEvent);
            google.maps.event.addListener(path, 'remove_at', $scope.broadcastOverlaysChangeEvent);
        });
        $scope.overlays.push(polygon);
        $scope.broadcastOverlaysChangeEvent();
    });

    $scope.drawingManager.setOptions({drawingControl: true});
}

function LandAddCtrl($scope) {

    LandAddEditBaseCtrl($scope);

    $scope.land = new $scope.Land();
    $scope.overlays = new OverlayArray();

    $scope.saveLand = function() {
        $scope.land.$save(function() {
            $scope.$location.path('/');
        }, function() {
            console.log('error adding');
        });
    };
}

function LandEditCtrl($scope, $routeParams) {

    LandAddEditBaseCtrl($scope);

    $scope.overlays = new OverlayArray();
    $scope.land = $scope.Land.get({key: $routeParams.key}, function() {
        $scope.land.deletable = true;
        $scope.overlays = OverlayArray.fromObj(JSON.parse($scope.land.features));
        $scope.overlays.setEditable(true);
        $scope.overlays.addListener($scope.broadcastOverlaysChangeEvent);
        $scope.overlays.setMap($scope.map);
        $scope.map.fitBounds($scope.overlays.getBounds());

        angular.forEach($scope.overlays, function(overlay) {
            if (overlay instanceof google.maps.Marker) {
                google.maps.event.addListener(overlay, 'click', function() {
                    var infoWindow = new google.maps.InfoWindow({
                        content: document.getElementById('info')
                    });
                    infoWindow.open($scope.map, overlay);
                });
            }
        });
    });

    $scope.saveLand = function() {
        $scope.land.$update(function() {
            $scope.$location.path('/');
        }, function() {
            console.log('error updating');
        });
    };

    $scope.deleteLand = function() {
        $scope.land.$delete(function() {
            $scope.$location.path('/');
        }, function() {
            console.log('error deleting');
        });
    };
}