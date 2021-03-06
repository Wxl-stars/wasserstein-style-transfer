from torch import optim
from tqdm.auto import tqdm

from style import steps


def get_optimizers(model, gen_img, args):
    # Convolutional parameters
    if args.distance == "wass":
        disc_opt = optim.Adam(model.disc_parameters(), lr=args.disc_lr)
    else:
        disc_opt = None

    # Image parameters for optimization
    img_opt = optim.Adam([gen_img.requires_grad_()], lr=args.lr)

    return img_opt, disc_opt


def transfer(args, gen_img, style_img, model):
    # Optimizers
    img_opt, disc_opt = get_optimizers(model, gen_img, args)

    # Losses
    style_losses, content_losses = [], []
    disc_losses, gp_losses = [], []

    # Train
    pbar = tqdm(range(0, args.steps), 'Style Transfer')
    for _ in pbar:
        if args.distance == "wass":
            # Optimize the discriminator
            disc_loss, gp_loss = steps.disc_step(model, disc_opt, gen_img, style_img)
            disc_losses.append(disc_loss)
            gp_losses.append(gp_loss)

        # Optimize over style and content
        style_loss, content_loss = steps.sc_step(model, img_opt, gen_img, args)
        style_losses.append(style_loss)
        content_losses.append(content_loss)

        # Clamp the values of updated input image
        gen_img.data.clamp_(0, 1)

        # Progress Bar
        pbar_str = f'Style: {style_losses[-1]:.1f} Content: {content_losses[-1]:.1f} '
        if args.distance == "wass":
            pbar_str += f'Disc: {disc_losses[-1]:.1f} GP: {gp_losses[-1]:.1f} '
        pbar.set_postfix_str(pbar_str)

    # Return losses
    loss_dict = {'style': style_losses, 'content': content_losses}
    if args.distance == "wass":
        loss_dict['disc'] = disc_losses
        loss_dict['gp'] = gp_losses

    return loss_dict
