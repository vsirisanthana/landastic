// Extend google.maps.Polygon
google.maps.Polygon.prototype.getBounds = function() {
    var bounds = new google.maps.LatLngBounds();
    var paths = this.getPaths();
    paths.forEach(function(path) {
        path.forEach(function(latLng) {
            bounds.extend(latLng);
        });
    });
    return bounds;
};


// Define OverlayArray
OverlayArray.prototype = new Array();


function OverlayArray(overlays) {
    var self = this;
    if (overlays) {
        overlays.forEach(function(overlay) {
            self.push(overlay);
        })
    }
}

OverlayArray.prototype.clear = function() {
    this.setMap(null);
    this.length = 0;
};

OverlayArray.prototype.getBounds = function() {
    var bounds = new google.maps.LatLngBounds();
    this.forEach(function(overlay) {
        if (overlay instanceof google.maps.Marker) {
            bounds.extend(overlay.getPosition());
        } else {
            bounds.union(overlay.getBounds());
        }
    });
    return bounds;
};

OverlayArray.prototype.setEditable = function(editable) {
    this.forEach(function(overlay) {
        if (overlay instanceof google.maps.Marker) {
            overlay.setDraggable(editable);
        } else {
            overlay.setEditable(editable);
        }
    });
};

OverlayArray.prototype.setMap = function(map) {
    this.forEach(function(overlay) {
        overlay.setMap(map);
    });
};

OverlayArray.prototype.addListener = function(handler) {
    this.forEach(function(overlay) {
        if (overlay instanceof google.maps.Marker) {
            google.maps.event.addListener(overlay, 'dragend', handler);
        } else if (overlay instanceof google.maps.Circle) {
            google.maps.event.addListener(overlay, 'radius_changed', handler);
            google.maps.event.addListener(overlay, 'center_changed', handler);
        } else if (overlay instanceof google.maps.Polygon) {
            angular.forEach(overlay.getPaths(), function(path) {
                google.maps.event.addListener(path, 'set_at', handler);
                google.maps.event.addListener(path, 'insert_at', handler);
                google.maps.event.addListener(path, 'remove_at', handler);
            });
        }
    });
};

OverlayArray.prototype.toObj = function() {
    return this.map(function(overlay) {
        return overlay.toObj();
    });
};

OverlayArray.fromObj = function(objs) {
    return new OverlayArray(objs.map(function(obj) {
        var type = obj.type;
        if (type == 'Point') {
            return google.maps.Marker.fromObj(obj);
        } else if (type == 'Circle') {
            return google.maps.Circle.fromObj(obj);
        } else if (type == 'Polygon') {
            return google.maps.Polygon.fromObj(obj);
        }
    }));
};
