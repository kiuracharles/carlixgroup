let tickets = [];

function fetchTickets(){

    fetch("/api/tickets")
    .then(res => res.json())
    .then(data => {

        tickets = data;
        renderTickets(tickets);
        renderCharts(tickets);

    });

}

const table = document.getElementById("ticketTable");
const searchInput = document.getElementById("searchInput");

function renderTickets(data){

    table.innerHTML = "";

    let total = data.length;
    let revenue = total * 200;
    let used = data.filter(t => t.used === 1).length;
    let remaining = total - used;

    document.getElementById("totalTickets").innerText = total;
    document.getElementById("revenue").innerText = "KSh " + revenue;
    document.getElementById("usedTickets").innerText = used;
    document.getElementById("remainingTickets").innerText = remaining;

    data.forEach(ticket => {

        const row = `
        <tr>
            <td>${ticket.name}</td>
            <td>${ticket.phone}</td>
            <td>${ticket.tournament}</td>
            <td class="${ticket.used ? 'used' : 'unused'}">
                ${ticket.used ? "Used" : "Valid"}
            </td>
        </tr>
        `;

        table.innerHTML += row;
    });

}

function renderCharts(data){

    let tournamentCount = {};
    let revenueData = {};

    data.forEach(ticket => {

        let t = ticket.tournament;

        tournamentCount[t] = (tournamentCount[t] || 0) + 1;
        revenueData[t] = (revenueData[t] || 0) + 200;

    });

    // Destroy old charts
    if(window.tChart) window.tChart.destroy();
    if(window.rChart) window.rChart.destroy();

    // 🎟 Tournament Chart
    const ctx1 = document.getElementById("tournamentChart");

    window.tChart = new Chart(ctx1, {
        type: "bar",
        data: {
            labels: Object.keys(tournamentCount),
            datasets: [{
                label: "Tickets Sold",
                data: Object.values(tournamentCount)
            }]
        }
    });

    // 💰 Revenue Chart
    const ctx2 = document.getElementById("revenueChart");

    window.rChart = new Chart(ctx2, {
        type: "pie",
        data: {
            labels: Object.keys(revenueData),
            datasets: [{
                data: Object.values(revenueData)
            }]
        }
    });

}

// 🔍 SEARCH (SAFE)
if(searchInput){
    searchInput.addEventListener("input", () => {

        const value = searchInput.value.toLowerCase();

        const filtered = tickets.filter(t =>
            t.name.toLowerCase().includes(value) ||
            t.ticket_ref.toLowerCase().includes(value) ||
            t.tournament.toLowerCase().includes(value)
        );

        renderTickets(filtered);
        renderCharts(filtered);

    });
}

fetchTickets();