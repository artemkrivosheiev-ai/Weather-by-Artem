const canvas = document.getElementById("effectsCanvas");
const ctx = canvas && canvas.getContext ? canvas.getContext("2d") : null;

function resize() {
    if(!canvas) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resize();
window.onresize = resize;

let particles = [];
let currentWeatherType = "sun";

class Particle {
    constructor(type) {
        this.type = type;
        this.reset();
    }

    reset() {
        this.x = Math.random() * canvas.width;
        this.y = this.type === "sun" ? Math.random() * canvas.height/2 : -Math.random() * canvas.height;
        this.size = this.type === "rain" ? Math.random()*2+1 : Math.random()*3+1;
        this.speed = this.type === "rain" ? Math.random()*4+4 : Math.random()*1+0.5;
        this.opacity = Math.random() * 0.5 + 0.2;
        this.length = this.type === "rain" ? Math.random()*15+10 : this.size;
    }

    update() {
        if(this.type === "rain") this.y += this.speed;
        else if(this.type === "snow") { this.y += this.speed; this.x += Math.sin(this.y/20); }
        else if(this.type === "sun") { this.y += 0.1; this.x += Math.sin(this.y/50); }
        else if(this.type === "mist") { this.y += this.speed*0.1; }

        if(this.y > canvas.height) this.reset();
    }

    draw() {
        if(!ctx) return;
        if(this.type === "rain") {
            ctx.strokeStyle = `rgba(174,194,224,${this.opacity})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(this.x, this.y);
            ctx.lineTo(this.x, this.y + this.length);
            ctx.stroke();
        } else {
            ctx.fillStyle = this.type === "sun" ? `rgba(255,255,150,${this.opacity})` : `rgba(255,255,255,${this.opacity})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);
            ctx.fill();
        }
    }
}

function setWeather(type) {
    currentWeatherType = type;
    let count = type === "rain" ? 200 : type === "snow" ? 150 : type === "mist" ? 100 : 80;
    particles = Array.from({length: count}, () => new Particle(type));
}

function animate() {
    if(!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => { p.update(); p.draw(); });
    requestAnimationFrame(animate);
}
animate();

function applyWeatherFromAPI(main) {
    if(!main) {
        setWeather("sun");
        return;
    }
    const m = main.toLowerCase();
    if(m.includes("rain") || m.includes("drizzle")) setWeather("rain");
    else if(m.includes("snow")) setWeather("snow");
    else if(m.includes("mist") || m.includes("fog") || m.includes("haze")) setWeather("mist");
    else setWeather("sun");
}









