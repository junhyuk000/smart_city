function updateRegNumber() {
    var birthday = document.getElementById("birthday").value;
    if (birthday) {
        var regNumber = birthday.replace(/-/g, "").substring(2);
        document.getElementById("regNumberInput").value = regNumber;
    }
}

function getGenderFromRegNumber(regNumberSuffix) {
    var genderDigit = parseInt(regNumberSuffix.charAt(0), 10);
    return genderDigit % 2 === 0 ? 'female' : 'male';
}

function handleSubmit(event) {
    event.preventDefault();

    var regNumberPrefix = document.getElementById("regNumberInput").value;
    var regNumberSuffix = document.getElementById("regNumberInput2").value;
    var regNumberFirstDigit = parseInt(regNumberSuffix.charAt(0), 10);

    if (regNumberFirstDigit > 4) {
        alert("유효하지 않은 주민등록번호입니다. 다시 입력해 주세요.");
        document.getElementById("regNumberInput2").value = "";
        return;
    }

    var totalRegNumber = regNumberPrefix + "-" + regNumberSuffix;
    var gender = getGenderFromRegNumber(regNumberSuffix);

    document.getElementById("genderField").value = gender;
    document.getElementById("totalRegNumberField").value = totalRegNumber;

    event.target.submit();
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const passwordInput = document.getElementById('password');
    const passwordError = document.getElementById('passwordError');

    form.addEventListener('submit', function(event) {
        const password = passwordInput.value;

        const hasTwoNumbers = (password.match(/\d/g) || []).length >= 2;
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        if (!hasTwoNumbers || !hasSpecialChar) {
            passwordError.style.display = 'block';
            event.preventDefault();
        } else {
            passwordError.style.display = 'none';
        }
    });

    // 실시간 검증을 위한 이벤트 리스너 추가
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        const hasTwoNumbers = (password.match(/\d/g) || []).length >= 2;
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        if (!hasTwoNumbers || !hasSpecialChar) {
            passwordError.style.display = 'block';
        } else {
            passwordError.style.display = 'none';
        }
    });
});