library(ggplot2)
####set the dictory#####
setwd("/study_UT/Cenik_group/BP/prostate_new/")
####read the plot file#####
exp = read.table("boxplot_group.txt",header=T,sep="\t")
exp_f = data.frame(exp)
give.n <- function(x){
  return(c(y = median(x)*1.05, label = length(x)))}

for(i in colnames(exp_f)[1:44]){
  print(i)
  test1 = ggplot(data=exp_f, aes(x=exp_f$somatic_type, y=exp_f[i][,1], 
                                 fill=exp_f$somatic_type)) + geom_boxplot(aes(fill=exp_f$somatic_type), alpha = 0.8, width = 0.5) +
    labs(title=paste(i,"Box Plot",sep=" "), 
         x="FPKM",
         y="Mutation Classification") +
    guides(fill=FALSE) + theme_bw() + theme(plot.title = element_text(hjust=0.5, size=30)) +
    ggrepel::geom_text_repel(aes(label = exp_f$laber), color = "black", size = 3, segment.color = "grey") +
    geom_point(aes(fill=exp_f$laber), size = 1, color = "dark grey")+
    stat_summary(fun.data = give.n, geom = "text", fun.y = sum, 
                 position = position_dodge(width = 1), size =5) + 
    ggsave(filename=paste(i,"_breast.png",sep=""),width = 21, height = 10) 
}
