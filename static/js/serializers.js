google.maps.Marker.prototype.getBounds = function() {
    var position = this.getPosition();
    return new google.maps.LatLngBounds(position, position);
};


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



function serializeOverlays(overlays) {
    return JSON.stringify(overlays.map(function(overlay) {
        return overlay.toObj();
    }));
}

function deserializeOverlays(serializedOverlays) {
    return JSON.parse(serializedOverlays).map(function(obj) {
        var type = obj.type;
        if (type == 'Point') {
            return google.maps.Marker.fromObj(obj);
        } else if (type == 'Circle') {
            return google.maps.Circle.fromObj(obj);
        }
    });
}

function getBounds(overlays) {
    var bounds = new google.maps.LatLngBounds();
    overlays.forEach(function(overlay) {
        bounds.union(overlay.getBounds());
    });
    return bounds;
}