
/* Scroll reveal animation */

const observer = new IntersectionObserver(entries => {
entries.forEach(entry => {
if(entry.isIntersecting){
entry.target.classList.add("show");
}
});
});

document.querySelectorAll(".card").forEach(el=>{
el.classList.add("hidden");
observer.observe(el);
});


/* 3D card tilt */

document.querySelectorAll(".card").forEach(card => {

card.addEventListener("mousemove", e => {

const rect = card.getBoundingClientRect();
const x = e.clientX - rect.left;
const y = e.clientY - rect.top;

const centerX = rect.width/2;
const centerY = rect.height/2;

const rotateX = (y - centerY)/15;
const rotateY = (centerX - x)/15;

card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;

});

card.addEventListener("mouseleave", ()=>{
card.style.transform = "rotateX(0) rotateY(0)";
});

});


/* Magnetic buttons */

document.querySelectorAll(".magnetic").forEach(btn=>{

btn.addEventListener("mousemove",e=>{

const rect = btn.getBoundingClientRect();
const x = e.clientX - rect.left - rect.width/2;
const y = e.clientY - rect.top - rect.height/2;

btn.style.transform = `translate(${x*0.2}px,${y*0.2}px)`;

});

btn.addEventListener("mouseleave",()=>{
btn.style.transform = "translate(0,0)";
});

});