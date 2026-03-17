/* COLLAPSIBLE SECTIONS */
function toggleSection(id) {

    const section = document.getElementById(id);

    section.classList.toggle("open");

    if(section.classList.contains("open")){
        localStorage.setItem(id, "open");
    } else {
        localStorage.setItem(id, "closed");
    }

}

/* ACTIVE NAV */
document.querySelectorAll(".nav-link").forEach(link=>{
    if(link.href === window.location.href){
        link.classList.add("active");
    }
});

/* RISK SCORE AUTO CALCULATION */
function calculateRisk(){
    const impact = parseInt(document.getElementById("impact").value);
    const likelihood = parseInt(document.getElementById("likelihood").value);
    const score = impact * likelihood;
    document.getElementById("score").innerText = score;
}

/* THEME SWITCH */
function toggleTheme() {
    const body = document.getElementById("appBody");

    if (body.classList.contains("dark")) {
        body.classList.remove("dark");
        body.classList.add("light");
        localStorage.setItem("theme", "light");
    } else {
        body.classList.remove("light");
        body.classList.add("dark");
        localStorage.setItem("theme", "dark");
    }

    // 🔥 FIX LEGEND COLOR PROPERLY
if (window.riskChartInstance) {
    window.riskChartInstance.destroy();
    window.location.reload();
}
}

/* AUTO REFRESH DASHBOARD */
setInterval(()=>{
    const el = document.getElementById("liveTime");
    if(el){
        el.innerText = new Date().toLocaleTimeString();
    }
},1000);

/* SEARCH FILTER */
function filterTable(inputId, tableId){
    const filter = document.getElementById(inputId).value.toLowerCase();
    document.querySelectorAll(`#${tableId} tbody tr`).forEach(row=>{
        row.style.display = row.innerText.toLowerCase().includes(filter) ? "" : "none";
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const savedTheme = localStorage.getItem("theme") || "dark";
    document.getElementById("appBody").classList.add(savedTheme);
});