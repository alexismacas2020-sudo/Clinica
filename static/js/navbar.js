document.addEventListener("DOMContentLoaded", () => {
  const navbar = document.querySelector("[data-navbar]");
  if (!navbar) return;

  const updateNavbar = () => navbar.classList.toggle("is-scrolled", window.scrollY > 16);
  updateNavbar();
  window.addEventListener("scroll", updateNavbar, { passive: true });

  const currentPath = `${window.location.pathname.replace(/\/$/, "")}/`;
  navbar.querySelectorAll(".nav-link[href]").forEach((link) => {
    const linkPath = new URL(link.href, window.location.origin).pathname.replace(/\/$/, "") + "/";
    const isHome = linkPath === "/" && currentPath === "/";
    const isSection = linkPath !== "/" && currentPath.startsWith(linkPath);
    if (isHome || isSection) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });

  const menu = navbar.querySelector("#menuNavbar");
  if (!menu || !window.bootstrap) return;
  menu.querySelectorAll("a:not(.dropdown-toggle)").forEach((link) => {
    link.addEventListener("click", () => {
      if (window.innerWidth < 1200 && menu.classList.contains("show")) {
        window.bootstrap.Collapse.getOrCreateInstance(menu).hide();
      }
    });
  });
});
