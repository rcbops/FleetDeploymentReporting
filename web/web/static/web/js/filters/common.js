// Converts integer bytes into human friendly values.
angular.module("cloudSnitch").filter("prettyStorageUnits", function() {

    const places = 2;
    const KiB = 1024;
    const MiB = KiB * KiB;
    const GiB = MiB * KiB;

    function render(value, unit) {
        return `${value.toFixed(places)} ${unit}`;
    }

    return function(sizeInBytes) {
        if (isNaN(sizeInBytes)) { return sizeInBytes; }
        if (sizeInBytes > GiB) { return render(sizeInBytes / GiB, "GiB"); }
        if (sizeInBytes > MiB) { return render(sizeInBytes / MiB, "MiB"); }
        if (sizeInBytes > KiB) { return render(sizeInBytes / KiB, "KiB"); }
        return render(sizeInBytes, "B");
    };
});
