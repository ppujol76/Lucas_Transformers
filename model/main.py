import torch
from torch import nn

#from encoder import Encoder
from model.encoder import Encoder_VGG16
from dataset.vocabulary import Vocabulary
from model.transformer.decoder import TransformerDecoder

class ImageCaptioningModel(nn.Module):
	def __init__(self, image_features_dim:int,embed_size:int, vocab:Vocabulary, caption_max_length:int,decoder_num_layers=8):
		super(ImageCaptioningModel, self).__init__()
		self.vocab = vocab
		self.vocab_size = len(self.vocab.word_to_index)
		self.encoder = Encoder_VGG16()
		self.decoder = TransformerDecoder(image_features_dim,vocab_size=self.vocab_size,embed_size=embed_size,num_layers=decoder_num_layers)
		self.caption_max_length = caption_max_length

#		self.init_weights()
	
	def init_weights(self):
		for p in self.decoder.parameters():
			if p.dim() > 1:
				nn.init.xavier_uniform_(p)

	def forward(self, images, captions):
		"""
		images => (batch_size, channels, W, H)
		captions => (batch_size, captions_length)
		"""
		images_features = self.encoder(images)
		images_features = images_features.permute(1,0,2)
		predictions = self.decoder.forward(images_features, captions)
		return predictions
	
	def inference(self, image):
		image_features = self.encoder(image)
		hidden = self.decoder.init_hidden(image.shape[0])
		
		if torch.cuda.is_available():
			word = torch.cuda.IntTensor([self.vocab.word_to_index['<START>']])
		else:
			word = torch.tensor(self.vocab.word_to_index['<START>'])
		sentence = [word.item()]
		attention_weights=[]
		for i in range(self.caption_max_length):
			alphas, weighted_features = self.attention.forward(image_features, hidden)
			predictions_t, hidden = self.decoder.forward(weighted_features, word, hidden)
			word = torch.argmax(predictions_t, dim=-1)
			if word[0].item()==self.vocab.word_to_index['<END>']:
				break
			sentence.append(word.item())
			attention_weights.append(alphas)
		if torch.cuda.is_available():
			sentence=torch.cuda.IntTensor(sentence[1:])
		else:
			sentence=torch.tensor(sentence[1:])
		sentence=self.vocab.generate_caption(sentence)
		return sentence, attention_weights