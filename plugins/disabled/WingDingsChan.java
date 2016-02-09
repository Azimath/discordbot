import java.util.HashMap;
import java.util.Map;

//Commented code is unnecessary due to command-line args being separated by spaces.

public class WingDingsChan {

    static String[] encodeWingDings (String originalMessage) {
        char[] messageCharacters = new char [originalMessage.length()];
        for (int i = 0; i < messageCharacters.length; i++) {
            messageCharacters[i] = originalMessage.charAt(i);
        }
        String[] translatedCharacters = new String [originalMessage.length()];
        Map<Character, String> characterCodes = new HashMap<Character, String> ();

        characterCodes.put('A', ":v:");
        characterCodes.put('B', ":ok_hand:");
        characterCodes.put('C', ":thumbsup:");
        characterCodes.put('D', ":thumbsdown:");
        characterCodes.put('E', ":point_left:");
        characterCodes.put('F', ":point_right:");
        characterCodes.put('G', ":point_up:");
        characterCodes.put('H', ":point_down:");
        characterCodes.put('I', ":wave:");
        characterCodes.put('J', ":smiley:");
        characterCodes.put('K', ":neutral_face:");
        characterCodes.put('L', ":frowning:");
        characterCodes.put('M', ":bomb:");
        characterCodes.put('N', ":skull:");
        characterCodes.put('O', ":checkered_flag:");
        characterCodes.put('P', ":triangular_flag_on_post:");
        characterCodes.put('Q', ":airplane:");
        characterCodes.put('R', ":sunny:");
        characterCodes.put('S', ":droplet:");
        characterCodes.put('T', ":snowflake:");
        characterCodes.put('U', ":heavy_division_sign:");
        characterCodes.put('V', ":heavy_plus_sign:");
        characterCodes.put('W', ":sparkle:");
        characterCodes.put('X', ":eight_pointed_black_star:");
        characterCodes.put('Y', ":six_pointed_star:");
        characterCodes.put('Z', ":crescent_moon:");

        characterCodes.put('a', ":cancer:");
        characterCodes.put('b', ":leo:");
        characterCodes.put('c', ":virgo:");
        characterCodes.put('d', ":libra:");
        characterCodes.put('e', ":scorpius:");
        characterCodes.put('f', ":sagittarius:");
        characterCodes.put('g', ":capricorn:");
        characterCodes.put('h', ":aquarius:");
        characterCodes.put('i', ":pisces:");
        characterCodes.put('j', ":two_men_holding_hands:");
        characterCodes.put('k', ":two_women_holding_hands:");
        characterCodes.put('l', ":black_circle:");
        characterCodes.put('m', ":white_circle:");
        characterCodes.put('n', ":black_small_square:");
        characterCodes.put('o', ":white_small_square:");
        characterCodes.put('p', ":black_square_button:");
        characterCodes.put('q', ":white_medium_square:");
        characterCodes.put('r', ":white_square_button:");
        characterCodes.put('s', ":small_orange_diamond:");
        characterCodes.put('t', ":large_orange_diamond:");
        characterCodes.put('u', ":large_blue_diamond:");
        characterCodes.put('v', ":diamond_shape_with_a_dot_inside:");
        characterCodes.put('w', ":small_blue_diamond:");
        characterCodes.put('x', ":negative_squared_cross_mark:");
        characterCodes.put('y', ":arrow_up_small:");
        characterCodes.put('z', ":loop:");

        characterCodes.put('1', ":open_file_folder:");
        characterCodes.put('2', ":page_facing_up:");
        characterCodes.put('3', ":page_with_curl:");
        characterCodes.put('4', ":clipboard:");
        characterCodes.put('5', ":card_index:");
        characterCodes.put('6', ":hourglass:");
        characterCodes.put('7', ":musical_keyboard:");
        characterCodes.put('8', ":video_game:");
        characterCodes.put('9', ":radio_button:");
        characterCodes.put('0', ":file_folder:");

        characterCodes.put('-', ":mailbox:");
        characterCodes.put('=', ":cd:");
        characterCodes.put('`', ":gemini:");
        characterCodes.put('~', ":soon:");
        characterCodes.put('!', ":black_nib:");
        characterCodes.put('@', ":pencil2:");
        characterCodes.put('#', ":haircut:");
        characterCodes.put('$', ":eyeglasses:");
        characterCodes.put('%', ":bell:");
        characterCodes.put('^', ":aries:");
        characterCodes.put('&', ":book:");
        characterCodes.put('*', ":envelope:");
        characterCodes.put('(', ":phone:");
        characterCodes.put(')', ":telephone_receiver:");
        characterCodes.put('_', ":taurus:");
        characterCodes.put('+', ":love_letter:");
        characterCodes.put('[', ":first_quarter_moon:");
        characterCodes.put(']', ":anchor:");
        characterCodes.put('{', ":white_flower:");
        characterCodes.put('}', ":end:");
        characterCodes.put('\\', ":u6307:");
        characterCodes.put('|', ":cherry_blossom:");
        characterCodes.put(';', ":minidisc:");
        characterCodes.put(':', ":computer:");
        characterCodes.put('\'', ":flashlight:");
        characterCodes.put('\"', ":scissors:");
        characterCodes.put(',', ":mailbox_closed:");
        characterCodes.put('<', ":floppy_disk:");
        characterCodes.put('.', ":mailbox_with_mail:");
        characterCodes.put('>', ":movie_camera:");
        characterCodes.put('/', ":mailbox_with_no_mail:");
        characterCodes.put('?', ":pencil:");
        characterCodes.put(' ', "       ");

        for (int i = 0; i < translatedCharacters.length; i++) {
            if (characterCodes.containsKey(messageCharacters[i])) {
                translatedCharacters[i] = (String) characterCodes.get(messageCharacters[i]);
            } else {
                translatedCharacters[i] = ":question:";
            }
        }
        return translatedCharacters;
    }

    static String decodeWingDings (String originalMessage) {
        String[] codeWords = originalMessage.split("::|:");
        char [] englishCharacters = new char [codeWords.length-1];
        Map<String, Character> characterCodes = new HashMap<String, Character> ();

        characterCodes.put("v", 'A');
        characterCodes.put("ok_hand", 'B');
        characterCodes.put("thumbsup", 'C');
        characterCodes.put("thumbsdown", 'D');
        characterCodes.put("point_left", 'E');
        characterCodes.put("point_right", 'F');
        characterCodes.put("point_up", 'G');
        characterCodes.put("point_down", 'H');
        characterCodes.put("wave", 'I');
        characterCodes.put("smiley", 'J');
        characterCodes.put("neutral_face", 'K');
        characterCodes.put("frowning", 'L');
        characterCodes.put("bomb", 'M');
        characterCodes.put("skull", 'N');
        characterCodes.put("checkered_flag", 'O');
        characterCodes.put("triangular_flag_on_post", 'P');
        characterCodes.put("airplane", 'Q');
        characterCodes.put("sunny", 'R');
        characterCodes.put("droplet", 'S');
        characterCodes.put("snowflake", 'T');
        characterCodes.put("heavy_division_sign", 'U');
        characterCodes.put("heavy_plus_sign", 'V');
        characterCodes.put("sparkle", 'W');
        characterCodes.put("eight_pointed_black_star", 'X');
        characterCodes.put("six_pointed_star", 'Y');
        characterCodes.put("crescent_moon", 'Z');

        characterCodes.put("cancer", 'a');
        characterCodes.put("leo", 'b');
        characterCodes.put("virgo", 'c');
        characterCodes.put("libra", 'd');
        characterCodes.put("scorpius", 'e');
        characterCodes.put("sagittarius", 'f');
        characterCodes.put("capricorn", 'g');
        characterCodes.put("aquarius", 'h');
        characterCodes.put("pisces", 'i');
        characterCodes.put("two_men_holding_hands", 'j');
        characterCodes.put("two_women_holding_hands", 'k');
        characterCodes.put("black_circle", 'l');
        characterCodes.put("white_circle", 'm');
        characterCodes.put("black_small_square", 'n');
        characterCodes.put("white_small_square", 'o');
        characterCodes.put("black_square_button", 'p');
        characterCodes.put("white_medium_square", 'q');
        characterCodes.put("white_square_button", 'r');
        characterCodes.put("small_orange_diamond", 's');
        characterCodes.put("large_orange_diamond", 't');
        characterCodes.put("large_blue_diamond", 'u');
        characterCodes.put("diamond_shape_with_a_dot_inside", 'v');
        characterCodes.put("small_blue_diamond", 'w');
        characterCodes.put("negative_squared_cross_mark", 'x');
        characterCodes.put("arrow_up_small", 'y');
        characterCodes.put("loop", 'z');

        characterCodes.put("open_file_folder", '1');
        characterCodes.put("page_facing_up", '2');
        characterCodes.put("page_with_curl", '3');
        characterCodes.put("clipboard", '4');
        characterCodes.put("card_index", '5');
        characterCodes.put("hourglass", '6');
        characterCodes.put("musical_keyboard", '7');
        characterCodes.put("video_game", '8');
        characterCodes.put("radio_button", '9');
        characterCodes.put("file_folder", '0');

        characterCodes.put("mailbox", '-');
        characterCodes.put("cd", '=');
        characterCodes.put("gemini", '`');
        characterCodes.put("soon", '~');
        characterCodes.put("black_nib", '!');
        characterCodes.put("pencil2", '@');
        characterCodes.put("haircut", '#');
        characterCodes.put("eyeglasses", '$');
        characterCodes.put("bell", '%');
        characterCodes.put("aries", '^');
        characterCodes.put("book", '&');
        characterCodes.put("envelope", '*');
        characterCodes.put("phone", '(');
        characterCodes.put("telephone_receiver", ')');
        characterCodes.put("taurus", '_');
        characterCodes.put("love_letter", '+');
        characterCodes.put("first_quarter_moon", '[');
        characterCodes.put("anchor", ']');
        characterCodes.put("white_flower", '{');
        characterCodes.put("end", '}');
        characterCodes.put("u6307", '\\');
        characterCodes.put("cherry_blossom", '|');
        characterCodes.put("minidisc", ';');
        characterCodes.put("computer", ':');
        characterCodes.put("flashlight", '\'');
        characterCodes.put("scissors", '\"');
        characterCodes.put("mailbox_closed", ',');
        characterCodes.put("floppy_disk", '<');
        characterCodes.put("mailbox_with_mail", '.');
        characterCodes.put("movie_camera", '>');
        characterCodes.put("mailbox_with_no_mail", '/');
        characterCodes.put("pencil", '?');
        characterCodes.put(" ", ' ');

        for (int i = 0; i < englishCharacters.length; i++) {
            if (characterCodes.containsKey(codeWords[i+1])) {
                englishCharacters[i] = (char) characterCodes.get(codeWords[i+1]);
            } else {
                englishCharacters[i] = '¿';
            }
        }
        String decodedMessage = new String(englishCharacters);
        return decodedMessage;
    }

    public static void main (String[] args) {
        try {
            String originalMessage = args[0];
            int colonCount = originalMessage.length() - originalMessage.replace(":", "").length();
            if (colonCount % 2 == 0 
                    && colonCount != 0) {
                String decodedMessage = decodeWingDings(originalMessage);
                System.out.print(decodedMessage);
                System.err.print("1");
            } else {
                String[] translatedCharacters = encodeWingDings(originalMessage);
                StringBuilder characterCombiner = new StringBuilder();
                for (int i = 0; i < translatedCharacters.length; i++) {
                    characterCombiner.append(translatedCharacters[i]);
                }
                String translatedMessage = characterCombiner.toString();
                String[] spaceCorrection = translatedMessage.split("       ");
                StringBuilder plainTextCombiner = new StringBuilder();
                for (int i = 0; i < spaceCorrection.length; i++) {
                    plainTextCombiner.append(i != spaceCorrection.length-1 ? spaceCorrection[i]+" "
                            : spaceCorrection[i]);
                }
                //String plainText = "```"+translatedMessage+"```";
                String plainText = "```";
                plainText += plainTextCombiner.toString()+"```";
                System.out.print(translatedMessage);
                System.out.print("-");
                System.out.print(plainText);
                System.err.print("2");
            }
        } catch (Exception e) {
            System.out.print("ERROR: INVALID COMMAND-LINE ARGUMENT.");
            System.exit(0);
        }
    }

}
