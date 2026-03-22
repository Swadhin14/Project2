/* LOGIN */
console.log("script.js loaded");
function login() {
  localStorage.setItem("login", "yes");
  window.location = "upload.html";
}

/* SIGNUP */
function signup() {
  localStorage.setItem("Signup", "yes");
  window.location = "signup.html";
}

function signin() {
  let m = document.getElementById("msg");
  if (m) {
    m.innerText = "Sign up successful";
  }
  window.location = "login.html";
}

/* UPLOAD */
document.addEventListener("DOMContentLoaded", function () {
  const uploadBtn = document.getElementById("uploadBtn");
  const form = document.getElementById("uploadForm");

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
    });
  }

  if (uploadBtn) {
    uploadBtn.addEventListener("click", upload);
  }
});

async function upload() {
  let f = document.getElementById("resume");
  let m = document.getElementById("msg");
  let n = document.getElementById("nextBtn");

  if (f.files.length === 0) {
    m.innerText = "Select file first";
    return;
  }

  let file = f.files[0];
  let formData = new FormData();
  formData.append("file", file);

  m.innerText = "Uploading...";

  try {
    let response = await fetch("/api/upload-resume", {
      method: "POST",
      body: formData
    });

    let data = await response.json();

    if (!response.ok) {
      m.innerText = data.detail || "Upload failed";
      return;
    }

    m.innerText = data.message;
    n.disabled = false;

    localStorage.setItem("resume_filename", data.filename);
    localStorage.setItem("resume_text", data.text_preview);

  } catch (err) {
    console.error(err);
    m.innerText = "Server connection failed";
  }
}
/* NAVIGATION */
function goMock() {
  window.location = "mock.html";
}

function goDashboard() {
  window.location = "dashboard.html";
}

/* QUESTIONS */
let questions = [];
let index = 0;

document.addEventListener("DOMContentLoaded", async function() {
  if (document.getElementById("questionText")) {
     let progress = document.getElementById("progress");
     let qText = document.getElementById("questionText");
     
     // Only initialize questions if we are actually on the mock interview page
     if (qText.innerText.includes("Tell me about yourself") || qText.innerText.includes("Generating")) {
         qText.innerText = "Generating custom interview questions...";
         progress.innerText = "Please wait";
         
         let rText = localStorage.getItem("resume_text") || "Experienced Software Engineer";
         // Clear previous evaluations
         localStorage.setItem("evals", "[]");
         
         try {
           let res = await fetch("/api/interview/generate", {
             method: "POST",
             headers: { "Content-Type": "application/json" },
             body: JSON.stringify({ resume_text: rText })
           });
           let data = await res.json();
           questions = data.questions;
           updateQ();
         } catch(e) {
           console.error("Failed to generate questions:", e);
           questions = ["Tell me about yourself", "What are your strengths?", "Any questions for us?"];
           updateQ();
         }
     }
  }
});

/* TIMER - run only if timer element exists */
const timerEl = document.getElementById("timer");
if (timerEl) {
  let seconds = 0;
  setInterval(() => {
    seconds++;
    let m = Math.floor(seconds / 60);
    let s = seconds % 60;
    timerEl.innerText =
      `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }, 1000);
}

/* NEXT */
async function nextQ() {
  let answerBox = document.getElementById("answer");
  let ansText = answerBox ? answerBox.value : "";
  let currentQ = questions[index];
  
  let nextBtn = document.querySelector(".mock-controls .primary-btn");
  if (nextBtn) nextBtn.disabled = true;

  try {
     let res = await fetch("/api/interview/evaluate", {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ question: currentQ, answer: ansText })
     });
     let edata = await res.json();
     let currentEvals = JSON.parse(localStorage.getItem("evals") || "[]");
     currentEvals.push(edata);
     localStorage.setItem("evals", JSON.stringify(currentEvals));
  } catch(e) {
     console.error("Evaluation failed", e);
  }

  if (nextBtn) nextBtn.disabled = false;
  index++;

  if (index < questions.length) {
    updateQ();
  } else {
    window.location = "results.html";
  }
}

/* UPDATE QUESTION */
function updateQ() {
  let questionText = document.getElementById("questionText");
  let progress = document.getElementById("progress");
  let answer = document.getElementById("answer");

  if (questionText) {
    questionText.innerText = questions[index];
  }

  if (progress) {
    progress.innerText = `Question ${index + 1}/${questions.length || 5}`;
  }

  if (answer) {
    answer.value = "";
  }
}

/* END */
function endInterview() {
  window.location = "results.html";
}

/* LOGOUT */
function logout() {
  localStorage.clear();
  window.location = "index.html";
}

/* RESULT ANIMATION - run only if result bars exist */
window.onload = function () {
  let confBar = document.getElementById("confBar");
  let commBar = document.getElementById("commBar");
  let techBar = document.getElementById("techBar");
  let overallScore = document.getElementById("overallScore");

  if (confBar) {
     let storedEvals = JSON.parse(localStorage.getItem("evals") || "[]");
     let conf = 0, comm = 0, tech = 0;
     let len = storedEvals.length;
     
     if (len > 0) {
        for(let e of storedEvals) {
           conf += e.confidence || 70;
           comm += e.communication || 70;
           tech += e.technical || 70;
        }
        conf = Math.round(conf / len);
        comm = Math.round(comm / len);
        tech = Math.round(tech / len);
     } else {
        conf = 80; comm = 75; tech = 90;
     }

     // Animate bars
     setTimeout(() => {
         confBar.style.width = conf + "%";
         commBar.style.width = comm + "%";
         techBar.style.width = tech + "%";
     }, 300);
     
     if (overallScore) {
         let avg = Math.round((conf + comm + tech) / 3);
         overallScore.innerText = avg + "%";
         
         // Display recent feedback
         let feedbackBox = document.querySelector(".feedback p");
         if (feedbackBox && len > 0) {
             feedbackBox.innerText = storedEvals[len - 1].feedback || "Great attempt. Focus on clarity and concise technical details.";
         }
     }
  }
}