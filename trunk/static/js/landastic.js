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
            when('/add', {template: 'partials/add.html', controller: LandAddCtrl}).
            when('/edit/:key', {template: 'partials/add.html', controller: EditLandCtrl}).
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
            drawingModes: [google.maps.drawing.OverlayType.MARKER]
        },
        markerOptions: {
            draggable: true
        }
    });
    $scope.drawingManager.setMap($scope.map);

    google.maps.event.addListener($scope.drawingManager, 'overlaycomplete', function(event) {
        if (event.type == google.maps.drawing.OverlayType.MARKER) {
            var position = event.overlay.getPosition();
            $scope.activeLand.location = position.lat() + ',' + position.lng();
            $scope.$apply();
        }
    });


//    if ($location.path() == '/') {
//        console.log(
//    } else {
//        console.log($location.path());
//    }

    $scope.$watch('lands.length', function(newValue, oldValue) {
//        console.log('lands length changed');
        $scope.refreshLandOverlays();
//        console.log('lands length changed done');
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
        $scope.activeLand = new $scope.Land();
        $scope.drawingManager.setOptions({drawingControl: true});
//        $scope.lands = [];
    };

    $scope.landEditView = function(land) {
        $scope.activeLand = angular.copy(land);
        $scope.drawingManager.setOptions({drawingControl: true});
    }


//    if ($location == '/') {
//        $scope.landListView();
//    } else if ($location == '/add') {
//        $scope.landAddView();
//    } else {
//        $scope.landListView();
//        $scope.landEditView()
//    }


//    $scope.lands = $scope.Land.query({}, function() {
//        $scope.refreshLandOverlays();
//    });

//    $scope.activeLand = new $scope.Land();


    $scope.saveLand = function() {

        console.log('saving land key: ' + $scope.activeLand.key);

        if (!$scope.activeLand.key) {

            $scope.activeLand.$save({}, function() {
//                $scope.lands.unshift($scope.activeLand);

                $scope.lands = $scope.Land.query({}, function() {
                    $scope.refreshLandOverlays();
                });

                $location.path('/');
            }, function() {
                console.log('error');
            });
        }

        else {
            $scope.activeLand.$update({}, function() {

//                for (attr in $scope.activeLand) {
//                    console.log(attr);
//
//                    $scope.master[attr] = $scope.activeLand[attr];
//                }

                $scope.lands = $scope.Land.query({}, function() {
                    $scope.refreshLandOverlays();
                });

                $location.path('/');
            });
        }
    };

//    $scope.addLand = function() {
//        $scope.activeLand = new $scope.Land();
//    };

//    $scope.editLand = function(land) {
//        $scope.master = land;
//        $scope.activeLand = angular.copy(land);
//
//        console.log($scope.activeLand.name);
//        $scope.activeLand = $scope.Land.get({key: land.key});
//    };

    $scope.deleteLand = function(land) {
        land.$delete();
    };





    // Land Overlays model and functions
    $scope.landOverlays = [];

    $scope.deleteLandOverlays = function() {
        if ($scope.landOverlays) {
            for (i in $scope.landOverlays) {
                $scope.landOverlays[i].setMap(null);
            }
            $scope.landOverlays.length = 0;
        }
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
//            marker.setMap($scope.map);
            $scope.landOverlays.push(marker);
        });
    };

    $scope.setBounds = function() {
        var bounds = new google.maps.LatLngBounds();
        angular.forEach($scope.landOverlays, function(overlay) {
//            console.log(overlay.position.toString());
            bounds.extend(overlay.position);
        });
        $scope.map.fitBounds(bounds);
    };

    $scope.refreshLandOverlays = function() {
        $scope.deleteLandOverlays();
        $scope.addLandOverlays();
        $scope.setBounds();
    };
};


function LandListCtrl($scope) {
    $scope.landListView();
}

function LandAddCtrl($scope) {
    $scope.landAddView();
}

function EditLandCtrl($scope, $routeParams, $location) {
    var land = $scope.Land.get({key: $routeParams.key}, function() {
        $scope.landEditView(land);
    });
}