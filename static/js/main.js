/* COLLAPSIBLE SECTIONS */
function toggleSection(id) {
    const section = document.getElementById(id);
    section.classList.toggle("open");
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
function toggleTheme(){
    document.body.classList.toggle("light-mode");
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