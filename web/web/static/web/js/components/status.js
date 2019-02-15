function StatusController(cloudSnitchApi, messagingService) {
    var self = this;

    function update() {
        self.busy = true;
        self.data = null;
        cloudSnitchApi.status().then(
            function(data) {
                self.data = data;
                self.busy = false;
            },
            function(resp) {
                self.busy = false;
                messagingService.error("status", "API ERROR", resp.status);
            }
        );
    }

    self.toggleJson = function() {
        self.showJson = !self.showJson;
    };

    self.$onInit = function() {
        self.busy = true;
        self.showJson = false;
        update();
    };
}

angular.module("cloudSnitch").component("status", {
    templateUrl: "/static/web/html/status.html",
    controller: ["cloudSnitchApi", "messagingService", StatusController],
    bindings: {}
});
