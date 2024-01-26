from pronunciation_dictionary import PronunciationDict, Pronunciations

from txt_utils.transcription import transcribe_text_using_dict


def test_component():
  dictionary = PronunciationDict()
  dictionary["test"] = Pronunciations()
  dictionary["test"][("T", "EST")] = 1.2
  dictionary["abc"] = Pronunciations()
  dictionary["abc"][("A", "BC")] = 1.3

  result = transcribe_text_using_dict("test abc\nxyz abc", dictionary)

  assert result == 'T|EST| |A|BC\nA|BC'
