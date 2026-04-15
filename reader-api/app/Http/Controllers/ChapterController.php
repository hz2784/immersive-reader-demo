<?php

namespace App\Http\Controllers;

use App\Models\Chapter;
use Illuminate\Http\Request;

class ChapterController extends Controller
{
    public function timings(int $id)
    {
        $chapter = Chapter::findOrFail($id);

        return response()->json([
            'chapter_id' => $chapter->id,
            'title' => $chapter->title,
            'audio_url' => $chapter->audio_url,
            'timings' => $chapter->timings_json,
        ]);
    }

    public function uploadTimings(Request $request, int $id)
    {
        $chapter = Chapter::findOrFail($id);

        $data = $request->validate([
            'duration' => ['required', 'numeric', 'min:0'],
            'paragraphs' => ['required', 'array', 'min:1'],
            'paragraphs.*.id' => ['required', 'string'],
            'paragraphs.*.text' => ['required', 'string'],
            'paragraphs.*.words' => ['required', 'array'],
            'paragraphs.*.words.*.text' => ['required', 'string'],
            'paragraphs.*.words.*.start' => ['required', 'numeric', 'min:0'],
            'paragraphs.*.words.*.end' => ['required', 'numeric', 'min:0'],
        ]);

        $chapter->timings_json = $data;
        $chapter->save();

        return response()->json([
            'chapter_id' => $chapter->id,
            'paragraph_count' => count($data['paragraphs']),
            'updated_at' => $chapter->updated_at,
        ]);
    }
}
