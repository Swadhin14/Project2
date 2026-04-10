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
         
         let rFile = localStorage.getItem("resume_filename") || "";
         // Clear previous evaluations
         localStorage.setItem("evals", "[]");
         
         try {
           let res = await fetch("/api/interview/generate", {
             method: "POST",
             headers: { "Content-Type": "application/json" },
             body: JSON.stringify({ filename: rFile })
           });
           let data = await res.json();
           questions = data.questions;
           updateQ();
           startTimer();
         } catch(e) {
           console.error("Failed to generate questions:", e);
           questions = ["Tell me about yourself", "What are your strengths?", "Any questions for us?"];
           updateQ();
           startTimer();
         }
     }
  }
});

/* TIMER - run only if timer element exists */
let timerInterval;
function startTimer() {
  const timerEl = document.getElementById("timer");
  if (timerEl && !timerInterval) {
    let seconds = 0;
    timerInterval = setInterval(() => {
      seconds++;
      let m = Math.floor(seconds / 60);
      let s = seconds % 60;
      timerEl.innerText =
        `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }, 1000);
  }
}

/* NEXT */
let evalPromises = [];

async function nextQ() {
  let answerBox = document.getElementById("answer");
  let ansText = answerBox ? answerBox.value : "";
  let currentQ = questions[index];
  let rFile = localStorage.getItem("resume_filename") || "";
  
  let nextBtn = document.querySelector(".mock-controls .primary-btn");
  
  const evaluateAnswer = async () => {
    try {
       let res = await fetch("/api/interview/evaluate", {
           method: "POST",
           headers: { "Content-Type": "application/json" },
           body: JSON.stringify({ filename: rFile, question: currentQ, answer: ansText })
       });
       let edata = await res.json();
       edata.question = currentQ;
       edata.user_answer = ansText;
       let currentEvals = JSON.parse(localStorage.getItem("evals") || "[]");
       currentEvals.push(edata);
       localStorage.setItem("evals", JSON.stringify(currentEvals));
    } catch(e) {
       console.error("Evaluation failed", e);
    }
  };

  let p = evaluateAnswer();
  evalPromises.push(p);

  index++;

  if (index < questions.length) {
    updateQ();
  } else {
    if (nextBtn) {
        nextBtn.disabled = true;
        nextBtn.innerText = "Finalizing Results...";
    }
    await Promise.all(evalPromises);
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
         
         // Display complete detailed feedback
         let feedbackBox = document.querySelector(".feedback p");
         if (feedbackBox) {
             feedbackBox.innerText = "Here is a detailed breakdown of your performance across all questions.";
         }
         
         let completeFeedbackContainer = document.getElementById("completeFeedback");
         if (completeFeedbackContainer && len > 0) {
             completeFeedbackContainer.innerHTML = ""; // Clear existing
             storedEvals.forEach((e, idx) => {
                 let itemDiv = document.createElement("div");
                 itemDiv.className = "feedback-detail-item";
                 itemDiv.style.marginBottom = "20px";
                 itemDiv.style.padding = "15px";
                 itemDiv.style.background = "rgba(255, 255, 255, 0.05)";
                 itemDiv.style.borderRadius = "8px";
                 
                 itemDiv.innerHTML = `
                     <h4 style="margin-top:0;">Question ${idx + 1}: ${e.question}</h4>
                     <p><strong>Your Answer:</strong> ${e.user_answer || "(No answer provided)"}</p>
                     <p><strong>Feedback:</strong> <span style="color: #ffcc00">${e.feedback || "Good effort."}</span></p>
                     <p><strong>Ideal Answer:</strong> <span style="color: #00fa9a">${e.ideal_answer || "N/A"}</span></p>
                 `;
                 completeFeedbackContainer.appendChild(itemDiv);
             });
         }
     }
  }

  /* DASHBOARD POPULATE */
  let dashInterviews = document.getElementById("dashInterviews");
  if (dashInterviews) {
      let storedEvals = JSON.parse(localStorage.getItem("evals") || "[]");
      dashInterviews.innerText = storedEvals.length;
      
      let dashScore = document.getElementById("dashScore");
      let total = 0;
      storedEvals.forEach(e => {
          let score = Math.round(((e.confidence || 70) + (e.communication || 70) + (e.technical || 70)) / 3);
          total += score;
      });
      let avg = storedEvals.length > 0 ? Math.round(total / storedEvals.length) : 0;
      dashScore.innerText = avg + "%";
      
      let dashResume = document.getElementById("dashResume");
      let rName = localStorage.getItem("resume_filename");
      if (rName) {
          // cleanly format the ugly UUID off the resume filename if present
          dashResume.innerText = rName.includes("_") ? rName.split("_").slice(1).join("_").substring(0, 20) + "..." : rName.substring(0, 20) + "...";
      }
      
      let dashFeedback = document.getElementById("dashFeedback");
      if (storedEvals.length > 0) {
          dashFeedback.innerText = storedEvals[storedEvals.length - 1].feedback;
      }
  }
}