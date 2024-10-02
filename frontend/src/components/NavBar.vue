<template>
    <nav class="navbar">
        <div class="title"> 
            <RouterLink to="/overview">價格追蹤小幫手</RouterLink>
        </div>
        <div class="menu-icon" @click="toggleMenu">
            &#9776;
        </div>
        <ul class="options" :class="{ 'show-menu': showMobileMenu }">
            <li><RouterLink to="/overview">物價概覽</RouterLink></li>
            <li><RouterLink to="/trending">物價趨勢</RouterLink></li>
            <li><RouterLink to="/news">相關新聞</RouterLink></li>
            <li v-if="!isLoggedIn"><RouterLink to="/login">登入</RouterLink></li>
            <li v-else @click="logout">Hi, {{getUserName}}! 登出</li>
        </ul>
    </nav>
</template>

<script>
import { useAuthStore } from '@/stores/auth';

export default {
    name: 'NavBar',
    data() {
        return {
            showMobileMenu: false
        };
    },
    computed: {
        isLoggedIn() {
            const userStore = useAuthStore();
            return userStore.isLoggedIn;
        },
        getUserName() {
            const userStore = useAuthStore();
            return userStore.getUserName;
        }
    },
    methods: {
        toggleMenu() {
            this.showMobileMenu = !this.showMobileMenu;
        },
        logout() {
            const userStore = useAuthStore();
            userStore.logout();
        }
    }
};
</script>

<style scoped>
.navbar {
    display: flex;
    justify-content: space-between;
    background-color: #f3f3f3;
    padding: 1.5em;
    height: 4.5em;
    width: 100%;
    align-items: center;
    box-shadow: 0 0 5px #000000;
}

.navbar .menu-icon {
    display: none;
    font-size: 2em;
    cursor: pointer;
}

/* Mobile Styles */
@media (max-width: 768px) {
    .navbar {
        flex-direction: row; /* 始终保持横向排列 */
        align-items: center;
    }
    
    .navbar .menu-icon {
        display: block;
        font-size: 2em;
        cursor: pointer;
        position: static; /* 保持和標題同一排 */
    }

    .navbar ul {
        display: none;
        flex-direction: column;
        width: 100%;
        background-color: #f3f3f3;
        padding: 1em 0;
    }

    .navbar ul.show-menu {
        display: flex;
    }

    .navbar li {
        margin: 1em 0;
        text-align: center;
        width: 100%;
    }
}
</style>
