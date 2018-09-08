/**
 * The details controller covers displaying object details.
 */
angular.module('cloudSnitch').controller('DetailsController', ['$scope', '$log', 'cloudSnitchApi', 'typesService', 'timeService', function($scope, $log, cloudSnitchApi, typesService, timeService) {

    $scope.f = undefined;
    $scope.obj = {};
    $scope.identity = "";
    $scope.children = {};
    $scope.busy = false;
    $scope.objectBusy = false;

    $scope.loadChildren = function() {
        var modelChildren = typesService.typeMap[$scope.f.type].children;
        $scope.children = {};

        angular.forEach(modelChildren, function(value, key) {
            $scope.children[key] = {
                label: value.label,
                records: [],
                show: false,
                busy: false
            }
            $scope.searchChildren(key, value.label);
        });
    };

    $scope.isBusy = function() {
        var busy = false;

        if ($scope.busy) { busy = true; }
        if ($scope.objectBusy) { busy = true; }
        angular.forEach($scope.children, function(childObj, childRef) {
            if (childObj.busy) { busy = true; }
        });
        return busy;
    };

    $scope.updateTimes = function() {
        if ($scope.f.times !== undefined)
            return;
        $scope.f.times = [];
        $scope.busy = true;
        cloudSnitchApi.times(
            $scope.f.type,
            $scope.identity,
            $scope.paneObj.search.time
        ).then(function(data) {
            for (var i = 0; i < data.times.length; i++) {
                var t = data.times[i];
                t = timeService.fromMilliseconds(t);
                t = t.local(t);
                t = timeService.str(t);
                $scope.f.times.push(t);
                $scope.busy = false;
            }
        }, function(resp) {
            $log.log("In promise failure updateTimes");
            $scope.$broadcast("notification:api",
                              {
                                 function: "updateTimes",
                                 message: resp.statusText,
                                 status: resp.status,
                                 subject: "times",
                                 type: "ERROR"
                              });
            $scope.busy = false;
        });
    };

    $scope.updateObject = function() {
        $scope.objectBusy = true;
        cloudSnitchApi.searchAll(
            $scope.f.type,
            $scope.identity,
            $scope.f.time,
            undefined,
            function(data) {
                if (data.records.length > 0) {
                    $scope.f.record = data.records[0];
                    $scope.obj = $scope.f.record[$scope.f.type];
                }
            }
        ).then(function(result) {
            $scope.objectBusy = false;
        }, function(resp) {
            $log.error("In promise failure updateObject");
            $scope.$broadcast("notification:api",
                              {
                                 function: "updateObject",
                                 message: resp.statusText,
                                 status: resp.status,
                                 subject: "searchAll",
                                 type: "ERROR"
                              });
            $scope.objectBusy = false;
        });
    };

    $scope.toggleChild = function(childObj) {
        childObj.show = !childObj.show;
    };

    $scope.searchChildren = function(childRef, childLabel) {
        $scope.children[childRef].records = [];
        $scope.children[childRef].busy = true;
        cloudSnitchApi.searchAll(
            childLabel,
            undefined,
            $scope.f.time,
            [{
                model: $scope.f.type,
                property: typesService.identityProperty($scope.f.type),
                operator: '=',
                value: $scope.identity
            }],
            function(data) {
                angular.forEach(data.records, function(item) {
                    $scope.children[childRef].records.push(item);
                });
            }
        ).then(function(result) {
            $scope.children[childRef].busy = false;
        }, function(resp) {
            // @TODO - error handling
            $log.error("In promise failure searchChildren");
            $scope.$broadcast("notification:api",
                              {
                                 function: "searchChildren",
                                 message: resp.statusText,
                                 status: resp.status,
                                 subject: "searchAll",
                                 type: "ERROR"
                              });
            $scope.children[childRef].busy = false;
        });
    };

    $scope.childHeaders = function(childObj) {
        var headers = typesService.glanceViews[childObj.label];
        return headers;
    };

    $scope.childValues = function(childObj, childRecord) {
        var props = typesService.glanceViews[childObj.label];
        var obj = childRecord[childObj.label];
        var values = [];
        for (var i = 0; i < props.length; i++) {
            values.push(obj[props[i]]);
        }
        return values;
    };

    /**
     * Initialize the details with object and object type.
     */
    $scope.update = function() {
        $scope.f = $scope.frame();
        $scope.obj = $scope.f.record[$scope.f.type];

        var prop = typesService.identityProperty($scope.f.type);
        if (prop !== undefined) {
            $scope.identity = $scope.obj[prop];
        }

        $scope.loadChildren();
        $scope.updateObject();
        $scope.updateTimes();
        if ($scope.f.time === undefined)
            $scope.f.time = $scope.paneObj.search.time;
    };

    $scope.$watch('paneObj.stack.length', function(newVal) {
        $scope.update();
    });

}]);
