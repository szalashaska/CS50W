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

  // On submit, send email
  document.querySelector("#compose-form").onsubmit = send_email;

  // Add event listener on archive and replay button
  document
    .querySelector("#email-archive")
    .addEventListener("click", archive_email);

  document
    .querySelector("#email-replay")
    .addEventListener("click", replay_email);
});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#show-email-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";

  // Clear out composition fields
  document.querySelector("#compose-recipients").value = "";
  document.querySelector("#compose-subject").value = "";
  document.querySelector("#compose-body").value = "";
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector("#emails-view").style.display = "block";
  document.querySelector("#compose-view").style.display = "none";
  document.querySelector("#show-email-view").style.display = "none";

  // Show the mailbox name
  document.querySelector("#emails-view").innerHTML = `<h3>${
    mailbox.charAt(0).toUpperCase() + mailbox.slice(1)
  }</h3>`;

  // Load emails to the box
  load_emails(mailbox);
}

function send_email() {
  // Get values from form
  const sender = document.querySelector("#compose-sender").value;
  const recipients = document.querySelector("#compose-recipients").value;
  const subject = document.querySelector("#compose-subject").value;
  const body = document.querySelector("#compose-body").value;

  // Prepare data
  const data = {
    recipients: recipients,
    subject: subject,
    body: body,
  };

  // Send data, log the sending status
  fetch("/emails", { method: "POST", body: JSON.stringify(data) })
    .then((response) => response.json())
    .then((result) => {
      console.log(result);
      if (result["error"]) {
        alert(result["error"]);
      }
    })
    .then(() => load_mailbox("sent"));

  // Redirect to send-box and prevent reloading of the page
  return false;
}

async function load_emails(mailbox) {
  // Fetch the emails from API and assign them to variable
  let emails;
  await fetch(`/emails/${mailbox}`)
    .then((response) => response.json())
    .then((data) => {
      emails = data;
    })
    .catch((error) => {
      console.log(error);
      return;
    });

  // Check if current mailbox is empty and inform user
  if (!emails[0]) {
    let message = document.createElement("div");
    message.innerHTML = `You have no messages in ${mailbox}.`;
    document.querySelector("#emails-view").append(message);
  }

  // Create switch cases, depending on the mailbox we are in
  switch (mailbox) {
    case "sent":
      // For each emial recived assign appropriate variables
      emails.forEach((email) => {
        let message = document.createElement("div");
        message.classList.add("mailbox-emails");
        message.id = email.id;

        // In case sendbox inform user where to email was send
        let htmlInput = `<p><b>From:</b> ${email.sender} <b>to:</b> ${email.recipients}</p>
                          <p><b>Subject:</b> ${email.subject}</p>
                          <p class="text-muted">${email.timestamp}</p>`;

        message.innerHTML = htmlInput;
        document.querySelector("#emails-view").append(message);

        // Add event listner, to open messeage after click
        message.addEventListener("click", () =>
          show_email(message.id, mailbox)
        );
      });
      break;
    // For other mailboxes
    default:
      // For each emial recived assign appropriate variables
      emails.forEach((email) => {
        let message = document.createElement("div");
        message.classList.add("mailbox-emails");
        message.id = email.id;

        let htmlInput = `<p><b>From:</b> ${email.sender}</p>
                          <p><b>Subject:</b> ${email.subject}</p>
                          <p class="text-muted">${email.timestamp}</p>`;

        message.innerHTML = htmlInput;
        document.querySelector("#emails-view").append(message);

        // Change emails background, if it was already read
        if (email.read) {
          message.classList.add("unread-background");
        }

        // Add event listner, to open messeage after click
        message.addEventListener("click", () =>
          show_email(message.id, mailbox)
        );
      });
      break;
  }
}

async function show_email(id, mailbox) {
  // Show email view and hide other views
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "none";
  document.querySelector("#show-email-view").style.display = "block";

  // Load emial into email variable
  let email;
  await fetch(`/emails/${id}`)
    .then((response) => response.json())
    .then((data) => {
      email = data;
    })
    .catch((error) => {
      console.log(error);
      return;
    });

  // Append email sections to html elements
  document.querySelector("#email-sender").innerHTML = email.sender;
  document.querySelector("#email-recipients").innerHTML = email.recipients;
  document.querySelector("#email-subject").innerHTML = email.subject;
  document.querySelector("#email-timestamp").innerHTML = email.timestamp;
  document.querySelector("#email-body").innerHTML = email.body;

  // Add email id to Archive and Replay button
  archiveButton = document.querySelector("#email-archive");
  archiveButton.dataset.emailid = email.id;
  document.querySelector("#email-replay").dataset.emailid = email.id;

  // Do not archive button in sendbox
  if (mailbox != "sent") {
    archiveButton.classList.remove("hidden");
    // In inbox let user archive email
    if (mailbox === "inbox") {
      archiveButton.innerHTML = "Archive";
      // Make email show as read
      fetch(`/emails/${id}`, {
        method: "PUT",
        body: JSON.stringify({ read: true }),
      });
      // In archivebox let user unarchive email
    } else {
      archiveButton.innerHTML = "Unarchive";
    }
  } else {
    // Hide button after switching boxes
    archiveButton.classList.add("hidden");
  }
}

async function archive_email() {
  // Select archive buttton
  let archiveButton = document.querySelector("#email-archive");
  var bool;
  // Check witch acton should be taken
  switch (archiveButton.innerHTML) {
    case "Archive":
      bool = true;
      break;
    case "Unarchive":
      bool = false;
      break;
    default:
      console.log("Archive operation went wrong");
      return;
  }
  // Feetch email id from button
  let id = archiveButton.dataset.emailid;

  // Archive email
  await fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({ archived: bool }),
  });

  // Load invox view
  load_mailbox("inbox");
}

async function replay_email() {
  // Select replay button
  let replayButton = document.querySelector("#email-replay");
  var id = replayButton.dataset.emailid;

  // Load emial to variable
  let email;
  await fetch(`/emails/${id}`)
    .then((response) => response.json())
    .then((data) => {
      email = data;
    })
    .catch((error) => {
      console.log(error);
      return;
    });

  // Show compose view and hide other views
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#show-email-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";

  // Pre populate composition fields
  document.querySelector("#compose-recipients").value = email.sender;
  // Check if message was alredy responded ("Re:")
  if (email.subject.slice(0, 3).toUpperCase() == "RE:") {
    document.querySelector("#compose-subject").value = `${email.subject}`;
  } else {
    document.querySelector("#compose-subject").value = `Re: ${email.subject}`;
  }
  document.querySelector(
    "#compose-body"
  ).value = `\n On ${email.timestamp} ${email.sender} wrote: \n ${email.body}`;
}
