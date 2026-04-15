<?php

namespace Database\Seeders;

use App\Models\Chapter;
use Illuminate\Database\Seeder;

class ChapterSeeder extends Seeder
{
    public function run(): void
    {
        $timings = json_decode(
            file_get_contents(base_path('../audio/word_timings.json')),
            true
        );

        Chapter::updateOrCreate(
            ['id' => 1],
            [
                'title' => 'Chapter 1',
                'audio_url' => '/ALWAYS_HERE_FOR_YOU_HALAHMY_CH001.mp3',
                'timings_json' => $timings,
            ]
        );

        Chapter::updateOrCreate(
            ['id' => 2],
            [
                'title' => 'Chapter 2',
                'audio_url' => '/ALWAYS_HERE_FOR_YOU_HALAHMY_CH002.mp3',
                'timings_json' => $timings,
            ]
        );
    }
}
