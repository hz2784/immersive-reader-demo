<?php

use App\Http\Controllers\ChapterController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

Route::get('/chapters/{id}/timings', [ChapterController::class, 'timings']);
Route::post('/chapters/{id}/timings', [ChapterController::class, 'uploadTimings']);
