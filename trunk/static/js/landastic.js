//angular.module('Landastic', ['ngResource']);

//angular.module('Landastic', ['ngResource']).
//    config(['$routeProvider', function($routeProvider) {
//        $routeProvider.
//            when('/', {template: 'partials/list.html', controller: LandsCtrl}).
//            when('/add', {template: 'partials/add.html', controller: LandsCtrl}).
//            otherwise({redirectTo: '/'});
//    }]);


angular.module('Landastic', ['ngResource']).
    config(['$routeProvider', function($routeProvider) {
        $routeProvider.
            when('/', {template: 'partials/list.html', controller: LandListCtrl}).
            when('/add', {template: 'partials/edit.html', controller: LandAddCtrl}).
            when('/edit/:key', {template: 'partials/edit.html', controller: LandEditCtrl}).
            otherwise({redirectTo: '/'});
    }]);

//angular.module('Landastic', ['ngResource']).
//    config(['$locationProvider', function($locationProvider) {
//        $locationProvider.html5Mode(false);
//        $locationProvider.hashPrefix('!');
//    }]);


//function initialize() {
//    var myOptions = {
//        center: new google.maps.LatLng(-34.397, 150.644),
//        zoom: 8,
//        mapTypeId: google.maps.MapTypeId.ROADMAP
//    };
//    var map = new google.maps.Map(document.getElementById("map_canvas"),
//        myOptions);
//}


function LandsCtrl($scope, $location, $resource, $routeParams) {

//    $scope.$location = $location;

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

    google.maps.event.addListener($scope.drawingManager, 'markercomplete', function(marker) {
        $scope.landGeom.push(marker);
        $scope.activeLand.geom = $scope.stringifying($scope.landGeom);

        var position = marker.getPosition();
        $scope.activeLand.location = position.lat() + ',' + position.lng();
        $scope.$apply();
    });

    google.maps.event.addListener($scope.drawingManager, 'circlecomplete', function(circle) {
        $scope.landGeom.push(circle);
        $scope.activeLand.geom = $scope.stringifying($scope.landGeom);
        $scope.$apply();
    });




    $scope.$watch('lands.length', function() {
        $scope.refreshLandOverlays();
    });

    // Views
    $scope.landListView = function() {
        $scope.lands = $scope.Land.query();
        $scope.drawingManager.setOptions({
            drawingMode: null,
            drawingControl: false
        });
    };

    $scope.landAddView = function() {
        $scope.hideLandOverlays();
        $scope.activeLand = new $scope.Land();
        $scope.drawingManager.setOptions({drawingControl: true});
    };

    $scope.landEditView = function(land) {
        $scope.hideLandOverlays();
        $scope.activeLand = angular.copy(land);
        $scope.drawingManager.setOptions({drawingControl: true});

        var location = land.location.split(',');
        var latLng = new google.maps.LatLng(location[0], location[1]);
        var marker = new google.maps.Marker({
            draggable: true,
            map: $scope.map,
            position: latLng,
            title: land.name
        });

        google.maps.event.addListener(marker, 'dragend', function() {
            console.log('new position: ' + marker.getPosition().toString());
            var position = marker.getPosition();
            $scope.activeLand.location = position.lat() + ',' + position.lng();

            $scope.activeLand.json = JSON.stringify(marker.toObj());

            $scope.$apply();
        });
    };



    $scope.deleteLand = function(land) {
        land.$delete();
    };



    // Land Overlays model and functions
    $scope.landOverlays = [];

    $scope.deleteLandOverlays = function() {
        angular.forEach($scope.landOverlays, function(landOverlay) {
            landOverlay.setMap(null);
        });
        $scope.landOverlays.length = 0;
    };

    $scope.hideLandOverlays = function() {
        angular.forEach($scope.landOverlays, function(landOverlay) {
            landOverlay.setMap(null);
        });
    };

    $scope.showLandOverlays = function() {
        angular.forEach($scope.landOverlays, function(landOverlay) {
            landOverlay.setMap($scope.map);
        });
    };

    $scope.addLandOverlays = function() {
        angular.forEach($scope.lands, function(land) {
            var location = land.location.split(',');
            var latLng = new google.maps.LatLng(location[0], location[1]);
            var marker = new google.maps.Marker({
                icon: '/static/img/drw-ToolCircleLarge.png',
                map: $scope.map,
                position: latLng,
                title: land.name
            });
            $scope.landOverlays.push(marker);
        });
    };

    $scope.setBounds = function() {
        var bounds = new google.maps.LatLngBounds();
        angular.forEach($scope.landOverlays, function(overlay) {
            bounds.extend(overlay.position);
        });
        $scope.map.fitBounds(bounds);
    };

    $scope.refreshLandOverlays = function() {
        $scope.deleteLandOverlays();
        $scope.addLandOverlays();
        $scope.setBounds();
    };


    $scope.landGeom = [];


    $scope.geomToObj = function(geom) {
        var result = [];
        for (i in geom) {
            result.push(geom[i].toObj());
        }
        return result;
    };

    $scope.stringifying = function(geom) {
        return JSON.stringify($scope.geomToObj(geom));
    };


};


function LandListCtrl($scope) {
    $scope.landListView();
}

function LandAddCtrl($scope, $location) {
    $scope.landAddView();

    $scope.saveLand = function() {
        $scope.activeLand.$save({}, function() {
            $scope.lands = $scope.Land.query();
            $location.path('/');
        }, function() {
            console.log('error adding');
        });
    };
}

function LandEditCtrl($scope, $routeParams, $location) {
    var land = $scope.Land.get({key: $routeParams.key}, function() {
        $scope.landEditView(land);
    });

    $scope.saveLand = function() {
        $scope.activeLand.$update({}, function() {
            $scope.lands = $scope.Land.query();
            $location.path('/');
        }, function() {
            console.log('error updating');
        });
    };
}