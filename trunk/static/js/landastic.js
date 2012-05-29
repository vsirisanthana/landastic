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

function LandAddEditBaseCtrl($scope, $http, $compile) {
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
        $scope.setMarkerEditable(marker);
        $scope.overlays.push(marker);
        $scope.broadcastOverlaysChangeEvent();
    });

    google.maps.event.addListener($scope.drawingManager, 'circlecomplete', function(circle) {
        $scope.setCircleEditable(circle);
        $scope.overlays.push(circle);
        $scope.broadcastOverlaysChangeEvent();
    });

    google.maps.event.addListener($scope.drawingManager, 'polygoncomplete', function(polygon) {
        $scope.setPolygonEditable(polygon);
        $scope.overlays.push(polygon);
        $scope.broadcastOverlaysChangeEvent();
    });

    $scope.drawingManager.setOptions({drawingControl: true});

    $scope.deleteActiveOverlay = function() {
        var conformation = confirm('Are you sure you want to delete this feature?');
        if (conformation && $scope.activeOverlay) {
            $scope.overlays.remove($scope.activeOverlay);
            $scope.activeOverlay.setMap(null);
            $scope.activeOverlay = null;
            $scope.activeInfoWindow.close();
            $scope.$broadcast('overlaysChange');
        }
    }

    $scope.getAndShowInfoWindow = function(overlay, position) {
        $http.get('/templates/partials/infoWindow.html').success(function(data, status, headers) {
            $scope.activeOverlay = overlay;
            if ($scope.activeInfoWindow) {
                $scope.activeInfoWindow.close();
            }
            $scope.activeInfoWindow = new google.maps.InfoWindow({
                content: $compile(data)($scope)[0],
                position: position
            });
            $scope.activeInfoWindow.open($scope.map);
        });
    };

    $scope.setOverlayEditable = function(overlay) {
        if (overlay instanceof google.maps.Marker) {
            $scope.setMarkerEditable(overlay);
        } else if (overlay instanceof google.maps.Circle) {
            $scope.setCircleEditable(overlay);
        } else if (overlay instanceof google.maps.Polygon) {
            $scope.setPolygonEditable(overlay);
        }
    };

    $scope.setMarkerEditable = function(marker) {
        marker.setDraggable(true);
        google.maps.event.addListener(marker, 'dragend', $scope.broadcastOverlaysChangeEvent);
        google.maps.event.addListener(marker, 'click', function() {
            $scope.getAndShowInfoWindow(marker, marker.getPosition());
        });
    };

    $scope.setCircleEditable = function(circle) {
        google.maps.event.addListener(circle, 'mouseover', function() { circle.setEditable(true); });
        google.maps.event.addListener(circle, 'mouseout', function() { circle.setEditable(false); });
        google.maps.event.addListener(circle, 'center_changed', $scope.broadcastOverlaysChangeEvent);
        google.maps.event.addListener(circle, 'radius_changed', $scope.broadcastOverlaysChangeEvent);
        google.maps.event.addListener(circle, 'click', function(mouseEvent) {
            $scope.getAndShowInfoWindow(circle, mouseEvent.latLng);
        })
    };

    $scope.setPolygonEditable = function(polygon) {
        google.maps.event.addListener(polygon, 'mouseover', function() { polygon.setEditable(true); });
        google.maps.event.addListener(polygon, 'mouseout', function() { polygon.setEditable(false); });

        angular.forEach(polygon.getPaths(), function(path) {
            google.maps.event.addListener(path, 'set_at', $scope.broadcastOverlaysChangeEvent);
            google.maps.event.addListener(path, 'insert_at', $scope.broadcastOverlaysChangeEvent);
            google.maps.event.addListener(path, 'remove_at', $scope.broadcastOverlaysChangeEvent);
        });

        google.maps.event.addListener(polygon, 'click', function(mouseEvent) {
            $scope.getAndShowInfoWindow(polygon, mouseEvent.latLng);
        })
    };
}

function LandAddCtrl($scope, $http, $compile) {

    LandAddEditBaseCtrl($scope, $http, $compile);

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

function LandEditCtrl($scope, $routeParams, $http, $compile) {

    LandAddEditBaseCtrl($scope, $http, $compile);

    $scope.overlays = new OverlayArray();
    $scope.land = $scope.Land.get({key: $routeParams.key}, function() {
        $scope.land.deletable = true;
        $scope.overlays = OverlayArray.fromObj(JSON.parse($scope.land.features));
        $scope.overlays.setMap($scope.map);
        $scope.map.fitBounds($scope.overlays.getBounds());
        angular.forEach($scope.overlays, function(overlay) { $scope.setOverlayEditable(overlay) });

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