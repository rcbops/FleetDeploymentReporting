angular.module("cloudSnitch").factory("typesService", ["$rootScope", "$log", "cloudSnitchApi", "messagingService", function($rootScope, $log, cloudSnitchApi, messagingService) {

    var service = {};
    service.types = [];
    service.typeMap = {};
    service.typesLoading = true;
    service.paths = {};
    service.pathsLoading = true;
    service.properties = {};

    service.glanceViews = {
        AptPackage: ["name", "version"],
        Configfile: ["path"],
        ConfiguredInterface: ["device"],
        Device: ["name"],
        Environment: ["name", "account_number"],
        GitRemote: ["name"],
        GitRepo: ["path"],
        GitUntrackedFile: ["path"],
        GitUrl: ["url"],
        Host: ["hostname"],
        Interface: ["device"],
        KernelModule: ["name"],
        KernelModuleParameter: ["name", "value"],
        Mount: ["mount"],
        NameServer: ["ip"],
        Partition: ["name"],
        PythonPackage: ["name", "version"],
        Uservar: ["name", "value"],
        Virtualenv: ["path"],
    };

    service.diffLabelView = {
        AptPackage: "name",
        ConfigFile: "name",
        ConfiguredInterface: "device",
        Device: "name",
        Environment: "name",
        GitRemote: "name",
        GitRepo: "path",
        GitUntrackedFile: "path",
        GitUrl: "url",
        Host: "hostname",
        Interface: "device",
        KernelModule: "name",
        KernelModuleParameter: "name",
        Mount: "mount",
        NameServer: "ip",
        Partition: "name",
        PythonPackage: "name",
        Uservar: "name",
        Virtualenv: "path"
    };

    var strOperators = [
        "=",
        "<",
        "<=",
        ">",
        ">=",
        "<>",
        "CONTAINS",
        "STARTS WITH",
        "ENDS WITH"
    ];

    var numericOperators = [
        "=",
        "<",
        "<=",
        ">",
        ">=",
        "<>"
    ];

    var boolOperators = [
        "=",
        "<>"
    ];

    service.glanceProperties = function(label) {
        return service.glanceViews[label];
    };

    /**
     * Update properties for types.
     */
    service.updateProperties = function() {
        service.properties = {};
        angular.forEach(service.typeMap, function(type, label) {
            service.properties[label] = [];
            angular.forEach(type.properties, function(prop_obj, prop_name) {
                service.properties[label].push(prop_name);
            });
            service.properties[label].sort();
        });
    };

    /**
     * Update paths for types.
     */
    service.updatePaths = function() {
        cloudSnitchApi.paths().then(function(result) {
            service.paths = result;
            service.pathsLoading = false;
        }, function(resp) {
            messagingService.error(
                "master_alert",
                "API ERROR",
                resp.status + " " + resp.statusText
            );
            service.paths = {};
        });
    };

    /**
     * Update types.
     */
    service.updateTypes = function() {
        service.typeMap = {};
        cloudSnitchApi.types().then(function(result) {
            // Save the result
            service.types = result;

            // Map the result
            for (var i = 0; i < service.types.length; i++) {
                service.typeMap[service.types[i].label] = service.types[i];
            }

            // Update properties.
            service.updateProperties();

            // Stop loading indicator.
            service.typesLoading = false;

        }, function(resp) {
            messagingService.error(
                "master_alert",
                "API ERROR",
                resp.status + " " + resp.statusText
            );
            service.types = [];
        });
    };

    /**
     * Get path for a label.
     */
    service.path = function(label) {
        var p = [];
        var path = service.paths[label];
        if (!angular.isDefined(path)) {
            return [];
        }
        for (var i = 0; i < path.length; i++) {
            p.push(path[i]);
        }
        p.push(label);
        return p;
    };

    /**
     * Get identity property for a label.
     */
    service.identityProperty = function(label) {
        var prop = undefined;
        var type = service.typeMap[label];
        if (type !== undefined) {
            prop = type.identity;
        }
        return prop;
    };

    /**
     * Get operators for a label and property.
     */
    service.operators = function(label, property) {
        var type;

        try {
            type = service.typeMap[label].properties[property].type;
        } catch (error) {
            return [];
        }

        switch(type) {
        case "bool":
            return boolOperators;
        case "int":
        case "float":
            return numericOperators;
        default:
            return strOperators;
        }
    };

    /**
     * Get the type of a property
     */
    service.propertyType = function(label, property) {
        var type;
        try {
            type = service.typeMap[label].properties[property].type;
        } catch (error) {
            type = "str";
        }
        return type;
    };

    /**
     * Determine if a property is a number property
     */
    service.isNumber = function(label, property) {
        var type = service.propertyType(label, property);
        if (type === "int" || type === "float") { return true; }
        return false;
    };

    service.update = function() {
        service.updateTypes();
        service.updatePaths();
    };

    service.isLoading = function() {
        return service.typesLoading || service.pathsLoading;
    };

    service.update();
    return service;
}]);
