/**
 * Service for interacting with complex query string parameters.
 *
 * Objects are converted to base64 encoded json strings.
 * To unset a parameter, set its value to null.
 */
angular.module("cloudSnitch").factory("paramService", ["$location", function($location) {
    var service = {};
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
    return service;
}]);
