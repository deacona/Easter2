from loguru import logger
import config
import tensorflow
import tensorflow as tf
import itertools
import numpy as np
from editdistance import eval as edit_distance
from tqdm import tqdm
from data_loader import data_loader
import tensorflow.keras.backend as K
import os
import jiwer

def select_model_weights():
    weights_dir = "../weights"
    weights_files = [x for x in os.listdir(weights_dir) if x.startswith("EASTER2--")]

    if config.SELECT_BEST_CER:
        sorted_files = sorted(weights_files, key=lambda x: float(x.split("--")[2].replace(".hdf5", "")), reverse=False)
    else:
        sorted_files = sorted(weights_files, key=lambda x: int(x.split("--")[1]), reverse=True)

    selected_filepath = os.path.join(weights_dir, sorted_files[0])
    logger.info(f"Selected model weights file: {selected_filepath}")

    return selected_filepath

def ctc_custom(args):
    y_pred, labels, input_length, label_length = args
    
    ctc_loss = K.ctc_batch_cost(
        labels, 
        y_pred, 
        input_length, 
        label_length
    )
    p = tensorflow.exp(-ctc_loss)
    gamma = 0.5
    alpha=0.25 
    return alpha*(K.pow((1-p),gamma))*ctc_loss

def load_easter_model(checkpoint_path):
    if checkpoint_path == "Empty":
        # checkpoint_path = config.BEST_MODEL_PATH
        checkpoint_path = select_model_weights()
    try:
        checkpoint = tensorflow.keras.models.load_model(
            checkpoint_path,
            custom_objects={'<lambda>': lambda x, y: y,
            'tensorflow':tf, 'K':K}
        )
        
        EASTER = tensorflow.keras.models.Model(
            checkpoint.get_layer('the_input').input,
            checkpoint.get_layer('Final').output
        )
    except:
        logger.info("Unable to Load Checkpoint.")
        return None
    return EASTER
    
def decoder(output,letters):
    ret = []
    for j in range(output.shape[0]):
        out_best = list(np.argmax(output[j,:], 1))
        out_best = [k for k, g in itertools.groupby(out_best)]
        outstr = ''
        for c in out_best:
            if c < len(letters):
                outstr += letters[c]
        ret.append(outstr)
    return ret
    
def test_on_iam(show = True, partition='test', uncased=False, checkpoint="Empty"):
        
    logger.info("loading metadata...")
    training_data = data_loader(config.DATA_PATH, config.BATCH_SIZE)
    validation_data = data_loader(config.DATA_PATH, config.BATCH_SIZE)
    test_data = data_loader(config.DATA_PATH, config.BATCH_SIZE)

    training_data.trainSet()
    validation_data.validationSet()
    test_data.testSet()
    charlist = training_data.charList

    logger.info("loading checkpoint...")
    model = load_easter_model(checkpoint)

    logger.info("calculating results...")
    char_error = 0
    total_chars = 0

    truth_list = []
    pred_list = []

    batches = 1
    while batches > 0:
        batches = batches - 1
        if partition == 'validation':
            logger.info("Using Validation Partition")
            imgs, truths, _ = validation_data.getValidationImage()
        else:
            logger.info("Using Test Partition")
            imgs,truths,_ = test_data.getTestImage()

        logger.info(f"Number of Samples : {len(imgs)}")
        for i in tqdm(range(0,len(imgs))):
            img = imgs[i]
            truth = truths[i].strip(" ").replace("  "," ")
            output = model.predict(img)
            prediction = decoder(output, charlist)
            output = (prediction[0].strip(" ").replace("  ", " "))
            
            if uncased:
                char_error += edit_distance(output.lower(),truth.lower())
                pred_list.append(output.lower())
                truth_list.append(truth.lower())
            else:
                char_error += edit_distance(output,truth)
                pred_list.append(output)
                truth_list.append(truth)
                
            total_chars += len(truth)
            if show:
                logger.info(f"Ground Truth :{truth}")
                logger.info(f"Prediction [{edit_distance(output,truth)}]  : {output}")
                logger.info("*"*50)
    cer_val = (char_error/total_chars)*100
    logger.info(f"Character error rate is : {cer_val}")

    char_metrics = jiwer.process_characters(truth_list, pred_list)
    logger.info(f"(JiWER) CER: {char_metrics.cer}")
    word_metrics = jiwer.process_words(truth_list, pred_list)
    logger.info(f"(JiWER) WER: {word_metrics.wer}")
    logger.info(f"(JiWER) MER: {word_metrics.mer}")
    logger.info(f"(JiWER) MIL: {word_metrics.wil}")
    logger.info(f"(JiWER) WIP: {word_metrics.wip}")