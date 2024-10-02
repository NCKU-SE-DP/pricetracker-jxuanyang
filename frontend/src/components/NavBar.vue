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

.navbar ul {
    list-style: none;
    display: flex;
    justify-content: space-around;
    margin-top: 1em; /* 預設情況下，將選單稍微下移 */
}

.navbar li {
    color: #575B5D;
    margin: 0 .5em;
    font-size: 1.2em;
}

.navbar li:hover {
    cursor: pointer;
    font-weight: bold;
}

.navbar a {
    text-decoration: none;
    color: #575B5D;
}

.title > a {
    font-size: 1.4em;
    font-weight: bold;
    color: #2c3e50 !important;
}

/* Mobile Styles */
@media (max-width: 768px) {
    .navbar {
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap; /* 允許元素換行 */
    }
    
    .navbar .menu-icon {
        display: block;
        font-size: 2em;
        cursor: pointer;
    }

    .navbar ul {
        display: none;
        flex-direction: column;
        width: 100%;
        background-color: #f3f3f3;
        padding: 1em 0;
        margin-top: 0; /* 重置 margin 以便下方顯示 */
    }

    .navbar ul.show-menu {
        display: flex;
        margin-top: 1em; /* 顯示時讓選單位於標題下方 */
    }

    .navbar li {
        margin: 1em 0;
        text-align: center;
        width: 100%;
    }
}
</style>
