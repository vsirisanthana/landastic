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
            when('/', {template: 'partials/list.html'}).
            when('/add', {template: 'partials/add.html'}).
            when('/edit/:key', {template: 'partials/add.html'}).
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


function LandsCtrl($scope, $location, $resource) {

    $scope.markers = [];

    var myOptions = {
        center: new google.maps.LatLng(-34.397, 150.644),
        zoom: 8,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    $scope.map = new google.maps.Map(document.getElementById("map_canvas"),
        myOptions);


    $scope.Land = $resource('/api/lands/:key', {key: '@key'}, {update: {method: 'PUT'}});


    $scope.$watch('lands.length', function(newValue, oldValue) {
        console.log('lands length changed');
    });

    $scope.lands = $scope.Land.query({}, function() {
        $scope.placeMarkers();
    });


    $scope.saveLand = function() {

        if (!$scope.active_land.key) {

            $scope.active_land.$save({}, function() {
//                $scope.lands.unshift($scope.active_land);

                $scope.lands = $scope.Land.query({}, function() {
                    $scope.placeMarkers();
                });

                $location.path('/');
            }, function() {
                console.log('error');
            });
        }

        else {
            $scope.active_land.$update({}, function() {

                for (attr in $scope.active_land) {
//                    console.log(attr);

                    $scope.master[attr] = $scope.active_land[attr];
                }

                $location.path('/');
            });
        }
    };

    $scope.addLand = function() {
        $scope.active_land = new $scope.Land();

//        $scope.map_span_size = 6;
//        $scope.lands_span_size = 0;
//        $scope.land_span_size = 6;
    };

    $scope.editLand = function(land) {
        $scope.master = land;
        $scope.active_land = angular.copy(land);
//        $scope.active_land = $scope.Land.get({key: land.key});
    };

    $scope.deleteLand = function(land) {
        land.$delete();
    };

    $scope.placeMarkers = function() {
        angular.forEach($scope.lands, function(land) {
            var latLng = land.location.split(',');
            var marker = new google.maps.Marker({
                position: new google.maps.LatLng(latLng[0], latLng[1]),
                title: land.name
            });
            marker.setMap($scope.map);

//            $scope.markers.push(marker);
        })

    }
};