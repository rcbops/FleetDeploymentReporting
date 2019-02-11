/**
 * Service for interacting with complex query string parameters.
 *
 * Objects are converted to base64 encoded json strings.
 * To unset a parameter, set its value to null.
 */
angular.module("cloudSnitch").factory("paramService", ["$location", function($location) {
    var service = {};

    /**
     * Set or unset a query string value.
     *
     * Used to convert complex objects into base64 encode json strings.
     */
    service.search = function(paramName, obj) {
        var val;
        // Set the value
        if(angular.isDefined(obj)) {
            if (obj !== null) {
                val = btoa(angular.toJson(obj));
            } else {
                val = obj;
            }
            $location.search(paramName, val);

        // Get the value
        } else {
            val = $location.search()[paramName];
            // Try to decode base64
            try {
                val = angular.fromJson(atob(val));
            }
            catch (e) {
                // Do nothing
            }
            return val;
        }
    };

    /**
     * Use when creating complex query string arguments manually.
     *
     * Example: when building links
     */
    service.manualEncode = function(obj) {
        return window.encodeURIComponent(btoa(angular.toJson(obj)));
    };

    return service;
}]);
