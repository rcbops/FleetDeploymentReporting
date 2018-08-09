function BigBusyController() {
    var self = this;
}

angular.module('cloudSnitch').component('bigbusy', {
    templateUrl: '/static/web/html/bigbusy.html',
    controller: BigBusyController,
    bindings: {
        busy: '<',
        text: '<',
    }
});
