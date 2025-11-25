document.addEventListener("DOMContentLoaded", function () {
    var sidebarToggle = document.querySelector(".pharma-sidebar-toggle");
    var sidebar = document.querySelector(".pharma-sidebar");
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            document.body.classList.toggle("pharma-sidebar-open");
        });
    }

    var userMenu = document.querySelector(".pharma-user-menu");
    var userToggle = document.querySelector(".pharma-user-toggle");
    if (userMenu && userToggle) {
        userToggle.addEventListener("click", function (e) {
            e.stopPropagation();
            userMenu.classList.toggle("open");
        });

        document.addEventListener("click", function () {
            userMenu.classList.remove("open");
        });
    }

    var dashboardData = document.getElementById("pharma-dashboard-data");
    if (dashboardData && typeof Chart !== "undefined") {
        var inStockValue = parseInt(dashboardData.dataset.inStock, 10) || 0;
        var outOfStockValue = parseInt(dashboardData.dataset.outOfStock, 10) || 0;

        var stockCanvas = document.getElementById("stockChart");
        if (stockCanvas) {
            new Chart(stockCanvas, {
                type: "doughnut",
                data: {
                    labels: ["In Stock", "Out of Stock"],
                    datasets: [
                        {
                            data: [inStockValue, outOfStockValue],
                            backgroundColor: ["#16a34a", "#dc2626"]
                        }
                    ]
                },
                options: {
                    plugins: {
                        legend: {
                            position: "bottom"
                        }
                    }
                }
            });
        }

        var categoryLabelsRaw = dashboardData.dataset.categoryLabels;
        var categoryCountsRaw = dashboardData.dataset.categoryCounts;

        var categoryLabels = [];
        var categoryCounts = [];

        if (categoryLabelsRaw) {
            try {
                categoryLabels = JSON.parse(categoryLabelsRaw);
            } catch (e) {
                categoryLabels = [];
            }
        }

        if (categoryCountsRaw) {
            try {
                categoryCounts = JSON.parse(categoryCountsRaw);
            } catch (e) {
                categoryCounts = [];
            }
        }

        var categoryCanvas = document.getElementById("categoryChart");
        if (categoryCanvas && categoryLabels.length > 0 && categoryCounts.length > 0) {
            new Chart(categoryCanvas, {
                type: "pie",
                data: {
                    labels: categoryLabels,
                    datasets: [
                        {
                            data: categoryCounts,
                            backgroundColor: [
                                "#1d4ed8",
                                "#22c55e",
                                "#f97316",
                                "#e11d48",
                                "#a855f7",
                                "#9ca3af"
                            ]
                        }
                    ]
                },
                options: {
                    plugins: {
                        legend: {
                            position: "bottom"
                        }
                    }
                }
            });
        }
    }


    
var drugAlert = document.getElementById("pharma-drug-alert");
if (drugAlert && typeof Swal !== "undefined") {
    var status = drugAlert.dataset.status || "";
    var message = drugAlert.dataset.message || "";

    if (message) {
        var lowerStatus = status.toLowerCase();
        var icon = "info";
        var title = "Update";

        if (lowerStatus.indexOf("success") !== -1) {
            icon = "success";
            title = "Success";
        } else if (lowerStatus.indexOf("error") !== -1 || lowerStatus.indexOf("danger") !== -1) {
            icon = "error";
            title = "Error";
        } else if (lowerStatus.indexOf("warning") !== -1) {
            icon = "warning";
            title = "Warning";
        }

        Swal.fire({
            icon: icon,
            title: title,
            text: message,
            timer: icon === "success" ? 2000 : undefined,
            showConfirmButton: icon === "success" ? false : true
        });
    }
}

});
