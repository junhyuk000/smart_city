// static/js/slider.js

// 다크모드 프리로드 (즉시 실행 - 페이지 로드 전에 실행됨)
(function() {
    // 로컬 스토리지에서 다크모드 설정 확인
    var darkMode = localStorage.getItem('darkMode');
    
    // 시스템 다크모드 설정 확인
    var prefersDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // 다크모드 설정이 있거나 시스템이 다크모드인 경우 미리 클래스 적용
    if (darkMode === 'enabled' || (darkMode === null && prefersDarkMode)) {
        document.documentElement.classList.add('dark-mode-preload');
        
        // body가 준비되면 다크모드 클래스 추가
        if (document.body) {
            document.body.classList.add('dark-mode');
        } else {
            document.addEventListener('DOMContentLoaded', function() {
                document.body.classList.add('dark-mode');
            });
        }
    }
    
    // 페이지 로드 완료 후 preload 클래스 제거
    window.addEventListener('load', function() {
        document.documentElement.classList.remove('dark-mode-preload');
    });
})();

// 페이지 로드 후 실행될 메인 코드
document.addEventListener('DOMContentLoaded', function() {
    // 다크 모드 토글 기능
    const initDarkMode = () => {
        const darkModeToggle = document.getElementById("dark-mode-toggle");
        const modeText = document.getElementById("mode-text");
        
        if (!darkModeToggle) return;
        
        // 현재 다크모드 상태 확인 - localStorage가 우선
        const savedMode = localStorage.getItem('darkMode');
        const isDarkMode = savedMode === 'enabled' || 
            (savedMode === null && window.matchMedia && 
             window.matchMedia('(prefers-color-scheme: dark)').matches);
        
        // body에 클래스 설정 - 페이지 로드시 한 번만 실행
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
            darkModeToggle.checked = true;
            if (modeText) modeText.textContent = "라이트모드";
        } else {
            document.body.classList.remove('dark-mode');
            darkModeToggle.checked = false;
            if (modeText) modeText.textContent = "다크모드";
        }
        
        // 토글 버튼 클릭 이벤트
        darkModeToggle.addEventListener("change", function() {
            const willBeDarkMode = this.checked;
            
            if (willBeDarkMode) {
                document.body.classList.add("dark-mode");
                localStorage.setItem("darkMode", "enabled");
                if (modeText) modeText.textContent = "라이트모드";
            } else {
                document.body.classList.remove("dark-mode");
                localStorage.setItem("darkMode", "disabled");
                if (modeText) modeText.textContent = "다크모드";
            }
            
            // 슬라이더 재초기화
            if (swiperInstance) {
                swiperInstance.update();
            }
        });
        
        // 시스템 테마 변경 감지 - 사용자 설정이 없을 때만 적용
        const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
        prefersDarkScheme.addEventListener('change', e => {
            if (!localStorage.getItem("darkMode")) {
                if (e.matches) {
                    document.body.classList.add("dark-mode");
                    darkModeToggle.checked = true;
                    if (modeText) modeText.textContent = "라이트모드";
                } else {
                    document.body.classList.remove("dark-mode");
                    darkModeToggle.checked = false;
                    if (modeText) modeText.textContent = "다크모드";
                }
            }
        });
    };

    // Swiper 슬라이더 초기화 (수정됨)
    const initSwiper = () => {
        const swiperContainer = document.querySelector('.swiper-container');
        if (!swiperContainer) return null;
        
        const swiper = new Swiper('.swiper-container', {
            // 기본 설정
            slidesPerView: 1,
            spaceBetween: 0,
            loop: true,
            speed: 800, // 슬라이드 전환 속도
            
            // 슬라이드 효과 사용
            effect: 'slide',
            
            // 자동 재생 설정
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
            },
            
            // 네비게이션 버튼 설정 - 화살표 버튼이 컨테이너 외부에 있음
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            
            // 페이지네이션 설정
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            
            // 오버플로우 처리
            watchOverflow: true,
            
            // 슬라이더가 화면 밖으로 나가지 않도록 설정
            observer: true,
            observeParents: true,
            
            // 슬라이드 효과를 더 부드럽게 만들기 위한 설정
            grabCursor: true,
            touchRatio: 1,
            touchAngle: 45,
            simulateTouch: true,
            
            // 접근성 개선
            a11y: {
                prevSlideMessage: '이전 슬라이드',
                nextSlideMessage: '다음 슬라이드',
                paginationBulletMessage: '{{index}}번 슬라이드로 이동',
                firstSlideMessage: '첫 번째 슬라이드',
                lastSlideMessage: '마지막 슬라이드',
            },
            
            // 키보드 네비게이션 활성화
            keyboard: {
                enabled: true,
                onlyInViewport: true,
            },
            
            // 터치 네비게이션 구성
            touchEventsTarget: 'container',
            touchStartPreventDefault: false, // 모바일에서 스크롤 방해 방지
        });
        
        // 슬라이더가 변경될 때 자동으로 포커스 유지
        swiper.on('slideChange', function() {
            const activeSlide = swiper.slides[swiper.activeIndex];
            if (activeSlide) {
                const slideImg = activeSlide.querySelector('img');
                if (slideImg) {
                    slideImg.setAttribute('aria-current', 'true');
                }
            }
        });
        
        return swiper;
    };
    
    // 스와이퍼 인스턴스 초기화
    let swiperInstance = initSwiper();
    
    // 이미지를 로드한 후 슬라이더 업데이트
    const updateSwiperAfterImagesLoaded = () => {
        const swiperContainer = document.querySelector('.swiper-container');
        if (!swiperContainer || !swiperInstance) return;
        
        const slides = document.querySelectorAll('.swiper-slide img');
        if (slides.length === 0) return;
        
        let loadedImages = 0;
        
        // 모든 이미지가 로드되면 업데이트
        const imageLoaded = () => {
            loadedImages++;
            if (loadedImages === slides.length) {
                swiperInstance.update();
            }
        };
        
        // 각 이미지에 로드 이벤트 리스너 추가
        slides.forEach(img => {
            if (img.complete) {
                imageLoaded();
            } else {
                img.addEventListener('load', imageLoaded);
                img.addEventListener('error', imageLoaded); // 이미지 오류 시에도 처리
            }
        });
    };
    
    if (swiperInstance) {
        updateSwiperAfterImagesLoaded();
        
        // 윈도우 리사이즈 시 슬라이더 업데이트
        window.addEventListener('resize', () => {
            if (swiperInstance) {
                swiperInstance.update();
            }
        });
    }
    
    // 로그인 필요 알림 기능 - 페이드인 효과 추가
    const initLoginAlert = () => {
        const loginRequiredLinks = document.querySelectorAll('.login-required');
        const loginAlert = document.getElementById('login-alert');
        
        if (loginRequiredLinks.length > 0 && loginAlert) {
            const goToLogin = document.getElementById('go-to-login');
            const closeAlertBtn = document.getElementById('close-alert-btn');
            
            // 로그인 필요 링크 클릭 이벤트
            loginRequiredLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // 페이드인 효과를 위한 표시 방식 변경
                    loginAlert.style.display = 'flex';
                    
                    // display 속성이 적용된 후에 애니메이션 시작을 위한 지연
                    setTimeout(() => {
                        loginAlert.classList.add('show');
                    }, 10);
                    
                    // 접근성 - 모달이 열렸을 때 포커스 이동
                    const focusableElements = loginAlert.querySelectorAll('button, [tabindex]:not([tabindex="-1"])');
                    if (focusableElements.length) {
                        setTimeout(() => {
                            focusableElements[0].focus();
                        }, 300);
                    }
                });
            });
            
            // 알림 닫기 이벤트 - 페이드아웃 효과 추가
            const closeLoginAlert = () => {
                loginAlert.classList.remove('show');
                
                // 페이드아웃 애니메이션이 끝난 후 display 속성 변경
                setTimeout(() => {
                    loginAlert.style.display = 'none';
                }, 400); // 트랜지션 시간과 동일하게 설정
            };
            
            if (closeAlertBtn) {
                closeAlertBtn.addEventListener('click', closeLoginAlert);
            }
            
            // 로그인 페이지로 이동 이벤트
            if (goToLogin) {
                goToLogin.addEventListener('click', function() {
                    window.location.href = "/login";
                });
            }
            
            // ESC 키로 알림 닫기
            window.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && loginAlert.style.display === 'flex') {
                    closeLoginAlert();
                }
            });
            
            // 모달 내에서 탭 키 트래핑
            loginAlert.addEventListener('keydown', function(e) {
                if (e.key === 'Tab' && loginAlert.style.display === 'flex') {
                    const focusableElements = loginAlert.querySelectorAll('button, [tabindex]:not([tabindex="-1"])');
                    const firstElement = focusableElements[0];
                    const lastElement = focusableElements[focusableElements.length - 1];
                    
                    // shift + tab
                    if (e.shiftKey) {
                        if (document.activeElement === firstElement) {
                            lastElement.focus();
                            e.preventDefault();
                        }
                    } 
                    // tab
                    else {
                        if (document.activeElement === lastElement) {
                            firstElement.focus();
                            e.preventDefault();
                        }
                    }
                }
            });
        }
    };
    
    // 플래시 메시지 처리 함수
    const handleFlashMessages = () => {
        const flashMessages = document.querySelectorAll('.flash-message');
        const container = document.getElementById('flash-messages-container');
        
        if (flashMessages.length > 0) {
            flashMessages.forEach(function(message) {
                message.classList.add('show');
                
                // 접근성 - 스크린 리더에게 알림
                message.setAttribute('role', 'alert');
                message.setAttribute('aria-live', 'assertive');
                
                // 닫기 버튼 추가
                if (!message.querySelector('.close-flash')) {
                    const closeBtn = document.createElement('button');
                    closeBtn.className = 'close-flash';
                    closeBtn.innerHTML = '&times;';
                    closeBtn.setAttribute('aria-label', '알림 닫기');
                    closeBtn.onclick = function() {
                        message.classList.remove('show');
                        setTimeout(() => {
                            if (document.body.contains(message)) {
                                message.remove();
                            }
                        }, 500);
                    };
                    
                    message.appendChild(closeBtn);
                }
                
                // 5초 후 메시지 숨기기
                setTimeout(function() {
                    if (document.body.contains(message)) {
                        message.classList.remove('show');
                        setTimeout(() => {
                            if (document.body.contains(message)) {
                                message.remove();
                            }
                        }, 500);
                    }
                }, 5000);
                
                // 컨테이너에 추가
                if (container) {
                    container.appendChild(message);
                }
            });
        }
    };
    
    // 위젯 접근성 개선
    const enhanceWidgetsAccessibility = () => {
        const widgets = document.querySelectorAll('.widget');
        widgets.forEach(widget => {
            // 위젯에 탭 인덱스 추가해 키보드 포커스 가능하게
            widget.setAttribute('tabindex', '0');
            
            // 키보드 인터랙션 처리
            widget.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    const link = this.querySelector('.widget-link');
                    if (link) {
                        e.preventDefault();
                        link.click();
                    }
                }
            });
        });
    };

    // Handle mobile menu toggle
    const initMobileMenu = () => {
        // Create a mobile menu toggle button
        const createMobileToggle = () => {
            if (document.querySelector('.mobile-menu-toggle')) return;
            
            const header = document.querySelector('.header-nav');
            if (!header) return;
            
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'mobile-menu-toggle';
            toggleBtn.setAttribute('aria-label', '메뉴 열기/닫기');
            toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
            
            // Only add mobile toggle in smaller screens
            if (window.innerWidth <= 768) {
                header.prepend(toggleBtn);
                
                toggleBtn.addEventListener('click', () => {
                    const navMenu = document.querySelector('.nav-menu');
                    if (navMenu) {
                        navMenu.classList.toggle('show-mobile-menu');
                        const isExpanded = navMenu.classList.contains('show-mobile-menu');
                        toggleBtn.setAttribute('aria-expanded', isExpanded);
                        
                        // Change icon based on state
                        toggleBtn.innerHTML = isExpanded ? 
                            '<i class="fas fa-times"></i>' : 
                            '<i class="fas fa-bars"></i>';
                    }
                });
            }
        };
        
        // Handle window resize for mobile menu
        const handleResize = () => {
            const navMenu = document.querySelector('.nav-menu');
            const toggleBtn = document.querySelector('.mobile-menu-toggle');
            
            if (window.innerWidth <= 768) {
                createMobileToggle();
                
                // Initialize dropdown click behavior on mobile
                initMobileDropdowns();
            } else {
                // Remove mobile menu toggle on larger screens
                if (toggleBtn) toggleBtn.remove();
                
                // Remove mobile-specific classes
                if (navMenu) {
                    navMenu.classList.remove('show-mobile-menu');
                }
                
                // Reset dropdown click handlers
                resetDropdowns();
            }
        };
        
        // Initialize mobile-friendly dropdowns
        const initMobileDropdowns = () => {
            const dropdownLinks = document.querySelectorAll('.nav-link-dropdown');
            
            dropdownLinks.forEach(link => {
                // Skip if already initialized
                if (link.dataset.mobileInitialized) return;
                
                link.dataset.mobileInitialized = 'true';
                
                link.addEventListener('click', function(e) {
                    if (window.innerWidth <= 768) {
                        e.preventDefault();
                        
                        // Find the dropdown content
                        const parent = this.closest('.menu-item');
                        if (parent) {
                            const dropdown = parent.querySelector('.dropdown-content');
                            if (dropdown) {
                                // Toggle dropdown visibility
                                const isVisible = dropdown.classList.contains('mobile-show');
                                
                                // Close all other dropdowns first
                                document.querySelectorAll('.dropdown-content').forEach(el => {
                                    el.classList.remove('mobile-show');
                                });
                                
                                // Toggle this dropdown
                                if (!isVisible) {
                                    dropdown.classList.add('mobile-show');
                                }
                            }
                        }
                    }
                });
            });
        };
        
        // Reset dropdowns when returning to desktop layout
        const resetDropdowns = () => {
            document.querySelectorAll('.dropdown-content').forEach(dropdown => {
                dropdown.classList.remove('mobile-show');
            });
        };
        
        // Add click handler to close dropdowns when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.menu-item') && window.innerWidth <= 768) {
                document.querySelectorAll('.dropdown-content').forEach(dropdown => {
                    dropdown.classList.remove('mobile-show');
                });
            }
        });
        
        // Initialize and set up resize handler
        createMobileToggle();
        handleResize();
        
        // Throttled resize handler
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(handleResize, 250);
        });
    };

    // Handle responsive sliders
    const enhanceResponsiveSlider = () => {
        const updateSliderHeight = () => {
            const swiperContainer = document.querySelector('.swiper-container');
            if (!swiperContainer) return;
            
            // Adjust height based on screen width
            if (window.innerWidth <= 400) {
                swiperContainer.style.height = '250px';
            } else if (window.innerWidth <= 576) {
                swiperContainer.style.height = '350px';
            } else if (window.innerWidth <= 768) {
                swiperContainer.style.height = '450px';
            } else if (window.innerWidth <= 1200) {
                swiperContainer.style.height = '550px';
            } else {
                swiperContainer.style.height = '650px';
            }
        };
        
        // Initialize
        updateSliderHeight();
        
        // Update on resize
        window.addEventListener('resize', updateSliderHeight);
    };
    
    // 초기화 함수 실행
    initDarkMode();
    initLoginAlert();
    handleFlashMessages();
    enhanceWidgetsAccessibility();
    initMobileMenu();
    enhanceResponsiveSlider();
});