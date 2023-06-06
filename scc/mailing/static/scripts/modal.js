$(function () {
    $("#button-modal").on("click", function (event) {
        document.getElementById("modal-window").style.display = "block";
    });
    $("#modal-close").on("click", function (event) {
        document.getElementById("modal-window").style.display = "none";
    });

    window.onclick = function (event) {
        console.log("click");
        let modal = document.getElementById("modal-window");
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
});