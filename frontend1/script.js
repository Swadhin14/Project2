/* LOGIN */
function login(){
localStorage.setItem("login","yes");
window.location="upload.html";
}
/* Signin*/
function signup(){
    localStorage.setItem("Signup","yes");
    window.location="signup.html";
}
function signin(){
    
    m=document.getElementById("msg");
    m.innerText="Sign up successful";
    window.location="login.html";
}

/* UPLOAD */
function upload(){
let f=document.getElementById("resume");
let m=document.getElementById("msg");
let n=document.getElementById("nextBtn");

if(f.files.length==0){
m.innerText="Select file first";
return;
}

m.innerText="Uploaded & synced ✅";
n.disabled=false;
}

/* NAVIGATION */
function goMock(){window.location="mock.html";}
function goDashboard(){window.location="dashboard.html";}

/* QUESTIONS */
let questions=[
"Tell me about yourself",
"Why should we hire you?",
"Your strengths?",
"Biggest challenge faced?",
"Where do you see yourself in 5 years?"
];

let index=0;

/* TIMER */
let seconds=0;
setInterval(()=>{
seconds++;
let m=Math.floor(seconds/60);
let s=seconds%60;
document.getElementById("timer").innerText=
`${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
},1000);

/* NEXT */
function nextQ(){
index++;

if(index<questions.length){
updateQ();
}else{
window.location="results.html";
}
}

// /* SKIP */
// function skipQ(){
// nextQ();
// }

/* UPDATE QUESTION */
function updateQ(){
document.getElementById("questionText").innerText=questions[index];
document.getElementById("progress").innerText=
`Question ${index+1}/5`;
document.getElementById("answer").value="";
}

/* END */
function endInterview(){
window.location="results.html";
}


/* LOGOUT */
function logout(){
localStorage.clear();
window.location="index.html";
}

/* RESULT ANIMATION */

window.onload = function(){

let conf=80;
let comm=75;
let tech=90;

document.getElementById("confBar").style.width = conf+"%";
document.getElementById("commBar").style.width = comm+"%";
document.getElementById("techBar").style.width = tech+"%";

}
