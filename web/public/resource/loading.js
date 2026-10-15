function addThemeColorCssVars() {
  const key = '__THEME_COLOR__'
  const defaultColor = '#8F2428'
  const themeColor = window.localStorage.getItem(key) || defaultColor
  document.documentElement.style.setProperty('--primary-color', themeColor)
}

addThemeColorCssVars()
