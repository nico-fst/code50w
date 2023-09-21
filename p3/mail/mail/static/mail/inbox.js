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

  document.querySelector("#compose-form").addEventListener("submit", send_mail);

  // By default, load the inbox
  load_mailbox("inbox");
});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";
  document.querySelector("#single-mail-view").style.display = "none";

  // Clear out composition fields
  document.querySelector("#compose-recipients").value = "";
  document.querySelector("#compose-subject").value = "";
  document.querySelector("#compose-body").value = "";
}

function send_mail(event) {
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
      console.log(result);
      load_mailbox("sent");
    });
  // .catch((error) => {
  // })
}

function view_mail(mail) {
  // Clear single-mail-view, show it and hide other views
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "none";
  document.querySelector("#single-mail-view").style.display = "block";
  document.querySelector("#single-mail-view").innerHTML = "";

  // Mark as read
  fetch(`/emails/${mail.id}`, {
    method: "PUT",
    body: JSON.stringify({ read: true }),
  });

  // Fetch Mail
  fetch(`/emails/${mail.id}`)
    .then((response) => response.json())
    .then((email) => {
      console.log(email);

      const header = document.createElement("div");
      header.innerHTML = `
          <strong>From: </strong>${mail.sender}<br>
          <strong>To: </strong>${mail.recipients}<br>
          <strong>Subject: </strong>${mail.subject}<br>
          <strong>Timestamp: </strong>${mail.timestamp}<br>
        `;

      const btn_archive_toggle = document.createElement("button");
      btn_archive_toggle.classList.add("btn", "btn-sm", "btn-outline-primary");
      btn_archive_toggle.textContent = mail.archived ? "Unarchive" : "Archive";
      btn_archive_toggle.addEventListener("click", function () {
        console.log("archive clicked");
        toggle_archive(mail);
      });
      const btn_reply = document.createElement("button");
      btn_reply.classList.add("btn", "btn-sm", "btn-outline-primary");
      btn_reply.textContent = "Reply";
      btn_reply.addEventListener("click", function () {
        console.log("reply clicked");
        reply(mail);
      });

      const body = document.createElement("pre");
      body.textContent = mail.body;

      // Add header, buttons and body to page
      document
        .querySelector("#single-mail-view")
        .append(header, btn_archive_toggle, btn_reply, document.createElement("hr"), body);
    });
}

function toggle_archive(mail) {
  fetch(`/emails/${mail.id}`, {
    method: "PUT",
    body: JSON.stringify({ archived: mail.archived ? false : true }),
  })
    .then((response) => {
      if (response.status === 204) {
        load_mailbox("inbox");
        console.log("Archiving status toggled successfully.");
      } else {
        throw new Error("API request failed with status: " + response.status);
      }
    })
    .catch((error) => {
      console.error("An error occurred:", error);
    });
}

function reply(mail) {
  compose_email();

  // Prefills
  document.querySelector("#compose-recipients").value = mail.sender;
  if (!mail.subject.startsWith("Re: ")) {
    // only add Re: once
    document.querySelector("#compose-subject").value = "Re: " + mail.subject;
  } else {
    document.querySelector("#compose-subject").value = mail.subject;
  }

  const bodyOld = mail.body.split('\n');
  const bodyOldIndented = bodyOld.map(line => `\t${line}`).join('\n');
  document.querySelector('#compose-body').value =
      `\n\n\tOn ${mail.timestamp} ${mail.sender} wrote:\n${bodyOldIndented}`;
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector("#emails-view").style.display = "block";
  document.querySelector("#compose-view").style.display = "none";
  document.querySelector("#single-mail-view").style.display = "none";

  // Show the mailbox name
  document.querySelector("#emails-view").innerHTML = `<h3>${
    mailbox.charAt(0).toUpperCase() + mailbox.slice(1)
  }</h3>`;

  // Show mails in mailbox
  fetch(`/emails/${mailbox}`)
    .then((response) => response.json())
    .then((emails) => {
      console.log(emails);

      emails.forEach(function (email) {
        const col = email.read ? "#E2E8F0" : "none";
        ediv = document.createElement("div");
        ediv.classList.add("mailItem");
        ediv.style.backgroundColor = col;
        ediv.innerHTML = `
            <span style="color: gray">${email.timestamp}</span><br>
            <strong>${email.sender}</strong><br>
            ${email.subject}
          `;
        ediv.addEventListener("click", function () {
          console.log(`"${email.subject}" clicked`);
          view_mail(email);
        });

        document.querySelector("#emails-view").append(ediv);
      });
    });
}
