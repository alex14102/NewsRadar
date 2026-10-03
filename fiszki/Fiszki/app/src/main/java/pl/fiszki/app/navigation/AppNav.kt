package pl.fiszki.app.navigation

import androidx.compose.runtime.Composable
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import pl.fiszki.app.data.Repository
import pl.fiszki.app.ui.screens.AddCardScreen
import pl.fiszki.app.ui.screens.DeckScreen
import pl.fiszki.app.ui.screens.HomeScreen
import pl.fiszki.app.ui.screens.StatsScreen
import pl.fiszki.app.ui.screens.StudyScreen
import pl.fiszki.app.ui.screens.ThemeScreen
import pl.fiszki.app.ui.theme.ThemeSettings
import pl.fiszki.app.ui.viewmodel.CardEditorViewModel
import pl.fiszki.app.ui.viewmodel.DeckViewModel
import pl.fiszki.app.ui.viewmodel.HomeViewModel
import pl.fiszki.app.ui.viewmodel.StatsViewModel
import pl.fiszki.app.ui.viewmodel.StudyViewModel

private fun NavController.openTab(route: String) {
    navigate(route) {
        popUpTo("home") { saveState = true }
        launchSingleTop = true
        restoreState = true
    }
}

/** Edytor: cardId ≥ 0 → edycja, inaczej nowa fiszka (deckId ≥ 0 → ta talia wybrana). */
private fun editorRoute(cardId: Long = -1L, deckId: Long = -1L) = "editor?cardId=$cardId&deckId=$deckId"

// ViewModele są tworzone per ekran (wpis na stosie nawigacji) i przeżywają np. obrót ekranu.
@Composable
fun AppNav(repo: Repository, settings: ThemeSettings, onSettings: (ThemeSettings) -> Unit) {
    val nav = rememberNavController()
    NavHost(navController = nav, startDestination = "home") {
        composable("home") {
            HomeScreen(
                vm = viewModel { HomeViewModel(repo) },
                onStudy = { id -> nav.navigate("study/$id") },
                onOpenDeck = { id -> nav.navigate("deck/$id") },
                onAdd = { nav.navigate(editorRoute()) },
                onTab = { nav.openTab(it) },
            )
        }
        composable(
            "study/{deckId}",
            arguments = listOf(navArgument("deckId") { type = NavType.LongType }),
        ) { entry ->
            val deckId = entry.arguments?.getLong("deckId") ?: -1L
            StudyScreen(
                vm = viewModel { StudyViewModel(repo, deckId) },
                onBack = { nav.popBackStack() },
            )
        }
        composable(
            "deck/{deckId}",
            arguments = listOf(navArgument("deckId") { type = NavType.LongType }),
        ) { entry ->
            val deckId = entry.arguments?.getLong("deckId") ?: -1L
            DeckScreen(
                vm = viewModel { DeckViewModel(repo, deckId) },
                onBack = { nav.popBackStack() },
                onStudy = { id -> nav.navigate("study/$id") },
                onAddCard = { id -> nav.navigate(editorRoute(deckId = id)) },
                onEditCard = { id -> nav.navigate(editorRoute(cardId = id)) },
            )
        }
        composable(
            "editor?cardId={cardId}&deckId={deckId}",
            arguments = listOf(
                navArgument("cardId") { type = NavType.LongType; defaultValue = -1L },
                navArgument("deckId") { type = NavType.LongType; defaultValue = -1L },
            ),
        ) { entry ->
            val cardId = entry.arguments?.getLong("cardId") ?: -1L
            val deckId = entry.arguments?.getLong("deckId") ?: -1L
            AddCardScreen(
                vm = viewModel { CardEditorViewModel(repo, cardId, deckId) },
                onDone = { nav.popBackStack() },
            )
        }
        composable("stats") {
            StatsScreen(vm = viewModel { StatsViewModel(repo) }, onTab = { nav.openTab(it) })
        }
        composable("theme") {
            ThemeScreen(settings = settings, onChange = onSettings, onTab = { nav.openTab(it) })
        }
    }
}
