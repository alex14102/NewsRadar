package pl.fiszki.app.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import pl.fiszki.app.data.Repository
import pl.fiszki.app.ui.screens.AddCardScreen
import pl.fiszki.app.ui.screens.HomeScreen
import pl.fiszki.app.ui.screens.StatsScreen
import pl.fiszki.app.ui.screens.StudyScreen
import pl.fiszki.app.ui.screens.ThemeScreen
import pl.fiszki.app.ui.theme.ThemeSettings

private fun NavController.openTab(route: String) {
    navigate(route) {
        popUpTo("home") { saveState = true }
        launchSingleTop = true
        restoreState = true
    }
}

@Composable
fun AppNav(repo: Repository, settings: ThemeSettings, onSettings: (ThemeSettings) -> Unit) {
    val nav = rememberNavController()
    NavHost(navController = nav, startDestination = "home") {
        composable("home") {
            HomeScreen(
                repo = repo,
                onStudy = { id -> nav.navigate("study/$id") },
                onAdd = { nav.navigate("add") },
                onTab = { nav.openTab(it) },
            )
        }
        composable(
            "study/{deckId}",
            arguments = listOf(navArgument("deckId") { type = NavType.LongType }),
        ) { entry ->
            StudyScreen(
                repo = repo,
                deckId = entry.arguments?.getLong("deckId") ?: -1L,
                onBack = { nav.popBackStack() },
            )
        }
        composable("add") {
            AddCardScreen(repo = repo, onDone = { nav.popBackStack() })
        }
        composable("stats") {
            StatsScreen(repo = repo, onTab = { nav.openTab(it) })
        }
        composable("theme") {
            ThemeScreen(settings = settings, onChange = onSettings, onTab = { nav.openTab(it) })
        }
    }
}
