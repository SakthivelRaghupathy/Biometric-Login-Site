/* ==========================================================
   BIOMETRIC LOGIN LANDING PAGE
   landing.js
========================================================== */

/* ===============================
   Navbar Shadow on Scroll
=============================== */

const navbar = document.querySelector(".custom-navbar");

window.addEventListener("scroll", () => {

    if (window.scrollY > 50) {

        navbar.classList.add("scrolled");

    } else {

        navbar.classList.remove("scrolled");

    }

});


/* ===============================
   Reveal Animation
=============================== */

const revealElements = document.querySelectorAll(
    ".feature-card, .security-box, .hero-card"
);

const revealOnScroll = () => {

    const triggerBottom = window.innerHeight * 0.85;

    revealElements.forEach((element) => {

        const elementTop = element.getBoundingClientRect().top;

        if (elementTop < triggerBottom) {

            element.classList.add("active");

        }

    });

};

window.addEventListener("scroll", revealOnScroll);

revealOnScroll();


/* ===============================
   Smooth Navigation
=============================== */

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        e.preventDefault();

        const target = document.querySelector(
            this.getAttribute("href")
        );

        if (target) {

            target.scrollIntoView({

                behavior: "smooth"

            });

        }

    });

});


/* ===============================
   Active Navbar Link
=============================== */

const sections = document.querySelectorAll("section");

const navLinks = document.querySelectorAll(".nav-link");

window.addEventListener("scroll", () => {

    let current = "";

    sections.forEach(section => {

        const sectionTop = section.offsetTop - 120;

        const sectionHeight = section.clientHeight;

        if (pageYOffset >= sectionTop) {

            current = section.getAttribute("id");

        }

    });

    navLinks.forEach(link => {

        link.classList.remove("active");

        if (link.getAttribute("href") === "#" + current) {

            link.classList.add("active");

        }

    });

});


/* ===============================
   Button Click Animation
=============================== */

const buttons = document.querySelectorAll(".btn");

buttons.forEach(button => {

    button.addEventListener("click", function () {

        this.style.transform = "scale(.96)";

        setTimeout(() => {

            this.style.transform = "";

        }, 120);

    });

});


/* ===============================
   Hero Card Mouse Effect
=============================== */

const heroCard = document.querySelector(".hero-card");

if (heroCard) {

    heroCard.addEventListener("mousemove", (e) => {

        const rect = heroCard.getBoundingClientRect();

        const x = e.clientX - rect.left;

        const y = e.clientY - rect.top;

        const rotateY = ((x / rect.width) - 0.5) * 10;

        const rotateX = ((y / rect.height) - 0.5) * -10;

        heroCard.style.transform =
            `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;

    });

    heroCard.addEventListener("mouseleave", () => {

        heroCard.style.transform =
            "rotateX(0deg) rotateY(0deg)";

    });

}


/* ===============================
   Console Message
=============================== */

console.log(
    "%cBiometric Login",
    "font-size:22px;font-weight:bold;color:#5B5FFF;"
);

console.log(
    "Landing Page Loaded Successfully."
);