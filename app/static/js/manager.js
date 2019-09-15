onclick = function(e) {
    if (e.target.tagName == "BUTTON" && e.target.classList.contains("delete")) {
        if (confirm("Really delete bot?")) {
            var req = new XMLHttpRequest();
            req.open("POST", "/delete");
            req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            req.send(JSON.stringify({
                "instance_id": e.target.getAttribute("instance_id"),
            }));
            req.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    location.reload();
                }
            };
        }
    }
};
