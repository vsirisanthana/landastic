angular.module('landasticServices', ['ngResource']).
    factory('Land', function($resource) {
        return $resource('/api/lands/:key', {key: '@key'}, {update: {method: 'PUT'}});
    });