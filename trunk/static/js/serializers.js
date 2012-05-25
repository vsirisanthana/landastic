google.maps.Marker.prototype.toObj = function() {
    var position = this.getPosition();
    return {
        type: 'Point',
        coordinates: [position.lat(), position.lng()]
    };
};

google.maps.Marker.fromObj = function(obj) {
    return new google.maps.Marker({
        position: new google.maps.LatLng(obj.coordinates[0], obj.coordinates[1])
    });
};

google.maps.Circle.prototype.toObj = function() {
    var center = this.getCenter();
    return {
        type: 'Circle',
        coordinates: [center.lat(), center.lng()],
        radius: this.getRadius()
    };
};

google.maps.Circle.fromObj = function(obj) {
    return new google.maps.Circle({
        center: new google.maps.LatLng(obj.coordinates[0], obj.coordinates[1]),
        radius: obj.radius
    });
};

google.maps.Polygon.prototype.toObj = function() {
    var _paths = [];
    this.getPaths().forEach(function(path) {
        var _path = [];
        path.forEach(function(latLng) {
            _path.push([latLng.lat(), latLng.lng()]);
        });
        _paths.push(_path);
    });
    return {
        type: 'Polygon',
        paths: _paths
    };
};

google.maps.Polygon.fromObj = function(obj) {
    return new google.maps.Polygon({
        paths: obj.paths.map(function(path) {
            return path.map(function(latLng) {
                return new google.maps.LatLng(latLng[0], latLng[1]);
            });
        })
    });
};
