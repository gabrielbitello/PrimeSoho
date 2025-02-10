document.addEventListener("DOMContentLoaded", function() {
    const formGroups = document.querySelectorAll(".form-group");

    formGroups.forEach(group => {
        const label = group.querySelector("label");
        const input = group.querySelector("input, select, textarea");

        if (label && input) {
            const labelWidth = label.offsetWidth;
            input.style.paddingLeft = `${labelWidth + 20}px`; // 20px de espaçamento adicional
        }
    });
});