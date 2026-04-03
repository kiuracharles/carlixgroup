// ✅ ALERT FUNCTION (GLOBAL)
function showAlert(message, type="success"){

    const alertBox = document.getElementById("customAlert");
    const alertMsg = document.getElementById("alertMessage");

    alertMsg.innerText = message;

    if(type === "error"){
        alertBox.style.background = "linear-gradient(135deg, #dc3545, #ff5c5c)";
    } else {
        alertBox.style.background = "linear-gradient(135deg, #007bff, #3399ff)";
    }

    alertBox.classList.add("show");

    setTimeout(() => {
        alertBox.classList.remove("show");
    }, 3000);
}


// 🎟 FORM SUBMIT
const form = document.getElementById("ticketForm")

form.addEventListener("submit", async function(e){

e.preventDefault()

const name = document.getElementById("name").value
const phone = document.getElementById("phone").value
const email = document.getElementById("email").value
const tournament = document.getElementById("tournament").value

const price = 2

// 🔥 replace alert()
showAlert("Sending M-Pesa payment request...")

const response = await fetch("/pay",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body: JSON.stringify({
name:name,
phone:phone,
email:email,
tournament:tournament,
amount:price
})

})

const data = await response.json()

if(data.status === "success"){

const ticketID = data.reference

document.getElementById("ticketTournament").innerText = tournament
document.getElementById("ticketName").innerText = "Name: " + name
document.getElementById("ticketID").innerText = "Ticket ID: " + ticketID
document.getElementById("ticketPrice").innerText = "Price: KSh 200"

const qrContainer = document.getElementById("qrcode")

qrContainer.innerHTML = ""

const ticketData = `
Tournament: ${tournament}
Name: ${name}
TicketID: ${ticketID}
Price: KSh 200
Carlix Group - THE KNOCKOUT
`

new QRCode(qrContainer,{
text:ticketData,
width:150,
height:150
})

// ✅ SUCCESS ALERT
showAlert("Payment successful! Ticket sent to your email. Can't see the email? check spam")

}else{

// ❌ ERROR ALERT
showAlert("Payment failed or cancelled", "error")

}

})

