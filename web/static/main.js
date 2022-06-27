const base = window.location.origin;

async function update() {
  const url = new URL("/api/update", base);
  const days = document.getElementById("days").value;
  const time = document.getElementById("time").value;
  const duration = document.getElementById("duration").value;
  url.searchParams.append("days", days);
  url.searchParams.append("time", time);
  url.searchParams.append("duration", duration);

  try {
    const response = await fetch(url);
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
  const url = new URL("/api/sleep", base);
  const duration = document.getElementById("duration-sleep").value;
  url.searchParams.append("duration", duration);
  try {
    const response = await fetch(url);
    const json = await response.json();
    document.getElementById("msg").innerHTML = "Done!";
    setTimeout(function(){
      document.getElementById("msg").innerHTML = "";
    }, 4000);
  } catch (error) {
    console.error('Error:', error);
  }
}
