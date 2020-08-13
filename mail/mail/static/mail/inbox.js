document.addEventListener("DOMContentLoaded", function () {
  // Use buttons to toggle between views
  document
    .querySelector("#inbox")
    .addEventListener("click", () => load_mailbox("inbox"));
  document
    .querySelector("#sent")
    .addEventListener("click", () => load_mailbox("sent"));
  document
    .querySelector("#archived")
    .addEventListener("click", () => load_mailbox("archive"));
  document.querySelector("#compose").addEventListener("click", compose_email);

  // By default, load the inbox
  load_mailbox("inbox");
});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";

  // Clear out composition fields
  document.querySelector("#compose-recipients").value = "";
  document.querySelector("#compose-subject").value = "";
  document.querySelector("#compose-body").value = "";

  // Send Mail feature
  document
    .querySelector("#compose-form")
    .addEventListener("submit", function (event) {
      event.preventDefault();
      fetch("/emails", {
        method: "POST",
        body: JSON.stringify({
          recipients: document.querySelector("#compose-recipients").value,
          subject: document.querySelector("#compose-subject").value,
          body: document.querySelector("#compose-body").value,
        }),
      })
        .then((response) => response.json())
        .then((result) => {
          if (result.message !== "Email sent successfully.") {
            alert(result.error);
          } else {
            load_mailbox("sent");
          }
        });
    });
}

function archive(id, flag) {
  fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      archived: !flag,
    }),
  });
  // add 0.1s delay to reflect updates in respective mailboxes properly
  setTimeout(load_mailbox, 100, "inbox");
}

function reply(email) {
  compose_email();
  let replyTitle = email.subject;
  if (!replyTitle.startsWith("Re: ")) {
    replyTitle = `Re: ${email.subject}`;
  }
  // Prefill composition fields
  document.querySelector("#compose-recipients").value = `${email.sender}`;
  document.querySelector("#compose-subject").value = replyTitle;
  document.querySelector(
    "#compose-body"
  ).value = `On ${email.timestamp} ${email.recipients} wrote:`;
}

function view_email(email_id, mailbox) {
  document.querySelector("#email-view").style.display = "block";
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "none";

  // mark mail read
  fetch(`/emails/${email_id}`, {
    method: "PUT",
    body: JSON.stringify({
      read: true,
    }),
  });

  // view mail content
  fetch(`/emails/${email_id}`)
    .then((response) => response.json())
    .then((email) => {
      document.querySelector(
        "#email-view"
      ).innerHTML = `<h2>${email.subject}</h2><h3>From: ${email.sender}</h3><h3>To: ${email.recipients}</h3><h4>${email.timestamp}</h4><br><div class=divider></div><br><span style="white-space: pre-line">${email.body}</span><div class=divider></div><br>`;
      if (mailbox !== "sent") {
        // implement archive feature
        const arch = document.createElement("BUTTON");
        arch.className = "btn btn-lg btn-outline-primary";
        const archiveFlag = email.archived;
        if (archiveFlag === true) {
          arch.innerHTML = "Unarchive Email";
        } else {
          arch.innerHTML = "Archive Email";
        }
        arch.addEventListener("click", () => archive(email_id, archiveFlag));
        document.querySelector("#email-view").append(arch);

        // implement reply feature
        const rep = document.createElement("BUTTON");
        rep.innerHTML = "Reply";
        rep.className = "btn btn-lg btn-outline-primary";
        rep.addEventListener("click", () => reply(email));
        document.querySelector("#email-view").append(rep);
      }
    });
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#emails-view").style.display = "block";
  document.querySelector("#compose-view").style.display = "none";

  // Show the mailbox name
  document.querySelector("#emails-view").innerHTML = `<h3>${
    mailbox.charAt(0).toUpperCase() + mailbox.slice(1)
  }</h3>`;

  fetch(`/emails/${mailbox}`)
    .then((response) => response.json())
    .then((emails) => {
      // Print emails
      emails.forEach((email) => {
        const box = document.createElement("div");
        // color mail box grey if read
        if (email.read === true && mailbox === "inbox") {
          box.style.backgroundColor = "grey";
        }
        box.className = "active";
        box.style.borderStyle = "solid";
        box.style.margin = "10px";
        box.style.padding = "10px";
        box.innerHTML = `<strong>${email.subject}</strong> </br> From: ${email.sender} </br> ${email.timestamp}`;
        box.addEventListener("click", () => view_email(email.id, mailbox));
        document.querySelector("#emails-view").append(box);
      });
    });
}
