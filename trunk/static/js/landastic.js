angular.module('Landastic', ['ngResource']);

function LandsCtrl($scope, $resource) {
    $scope.lands_api = $resource('/api/lands/:key',
        {},
        {
            getlist: { method: 'GET' },
            getinstance: { method: 'GET', params: {key: 'lands'}}
        }
    );
    var lands = $scope.lands_api.getlist({}, function() {
        $scope.lands = lands.results;
    });
};