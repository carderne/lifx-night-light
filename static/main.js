async function update() {
  const url = "/api/update";
  let days = document.getElementById("days").value;
  let time = document.getElementById("time").value;
  let duration = document.getElementById("duration").value;

  let data = {
    days: days,
    time: time,
    duration: duration
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json'
      }
    });
    const json = await response.json();
    document.getElementById("msg").innerHTML = "Done!";
    setTimeout(function(){
      document.getElementById("msg").innerHTML = "";
    }, 4000);
  } catch (error) {
    console.error('Error:', error);
  }
}

async function sleep() {
  const url = "/api/sleep";
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    const json = await response.json();
    document.getElementById("msg").innerHTML = "Done!";
    setTimeout(function(){
      document.getElementById("msg").innerHTML = "";
    }, 4000);
  } catch (error) {
    console.error('Error:', error);
  }
}
