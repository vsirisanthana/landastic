//angular.module('Landastic', ['ngResource']);

//angular.module('Landastic', ['ngResource']).
//    config(['$routeProvider', function($routeProvider) {
//        $routeProvider.
//            when('/', {template: 'partials/list.html', controller: LandsCtrl}).
//            when('/add', {template: 'partials/add.html', controller: LandsCtrl}).
//            otherwise({redirectTo: '/'});
//    }]);


//angular.module('Landastic', ['ngResource']).
//    config(['$routeProvider', function($routeProvider) {
//        $routeProvider.
//            when('/').
//            when('/add')
//            otherwise({redirectTo: '/'});
//    }]);

angular.module('Landastic', ['ngResource']).
    config(['$locationProvider', function($locationProvider) {
        $locationProvider.html5Mode(true);
        $locationProvider.hashPrefix('!');
    }]);


function initialize() {
    var myOptions = {
        center: new google.maps.LatLng(-34.397, 150.644),
        zoom: 8,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("map_canvas"),
        myOptions);
}


function LandsCtrl($scope, $location, $resource) {

//    $scope.$on('$afterRouteChange', function(ngEvent, route) {
//        console.log(route.template);
//    });

    $scope.$location = $location;

    $scope.map_span_size = 4;
    $scope.lands_span_size = 4;
    $scope.land_span_size = 4;

    $scope.Land = $resource('/api/lands/:key', {key: '@key'});

    $scope.lands = $scope.Land.query();

    $scope.saveLand = function() {

        var land = new $scope.Land({
            name: $scope.active_land.name,
            location: $scope.active_land.location
        })

        land.$save({}, function() {
            $scope.lands.unshift(land);
        }, function() {
            console.log('error');
        });

    };

    $scope.addLand = function() {
        $scope.active_land = new $scope.Land();

//        $scope.map_span_size = 6;
//        $scope.lands_span_size = 0;
//        $scope.land_span_size = 6;
    };

    $scope.editLand = function(land) {
        console.log('Editing land');
        $scope.active_land = land;
    };

    $scope.deleteLand = function(land) {
        land.$delete();
    };


};